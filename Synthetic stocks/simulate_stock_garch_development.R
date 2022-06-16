################
## LIBRARIES
################

library(quantmod)
library(rugarch)

################
## MACROS
################

TICKER = "GOOGL"
DATA_COLUMNS = c("open","high","low","close","volume","adjClose")
DATE_START = as.Date("2010-01-01")
DATE_END = as.Date("2022-06-01")
SEED = 123
N_SIM = 8

################
## FUNCTIONS
################

logdiff_to_orig = function(s,initial_val=1)
{
  return(initial_val*exp(cumsum(s)))
}

################
## MAIN
################

# get stock data
s = getSymbols(TICKER,from=DATE_START,to=DATE_END,auto.assign=F)

# transform to df
s = as.data.frame(s)

# rename columns
colnames(s) = DATA_COLUMNS

s2 = s

# log diff adj close
s2$logdiff = c(NA,diff(log(s2$adjClose)))

s2 = s2[2:nrow(s2),]
  
# fit gjr GARCH with normal distribution
mod_specify = ugarchspec(mean.model=list(armaOrder=c(0,0)),variance.model=list(model="gjrGARCH",garchOrder=c(1,1)),distribution.model="ssd")
mod_fitting = ugarchfit(data=s2$logdiff,spec=mod_specify)
mod_fitting
plot(mod_fitting)

### NOTE: pearson goodness-of-fit rejects normality and QQ-plot of standardized residuals show they are clearly non-normal. Use t-student.
mod_specify = ugarchspec(mean.model=list(armaOrder=c(0,0)),variance.model=list(model="gjrGARCH",garchOrder=c(1,1)),distribution.model="std")
mod_fitting = ugarchfit(data=s2$logdiff,spec=mod_specify)
mod_fitting

plot(mod_fitting)

### NOTE: using t-student distribution the goodness-of-fit test does not reject H0: residuals follow a t-student dist. 
### p-values of every coefficient is significant except for alpha1 with a p-value of approx. 0.2. 
plot(logdiff_to_orig(s2$logdiff,s2$adjClose[1]))
plot(s2$adjClose)

### Simulate

set.seed(SEED)

nsim = length(s2$logdiff)
dates = as.Date(rownames(s2),format="%Y-%m-%d")[1:nrow(s2)]

for (i in 1:N_SIM)
{
  # simulate
  x = ugarchsim(mod_fitting,n.sim=nsim, m.sim=1)
  
  # plots
  png(file=paste("sim_",i,".png",sep=""),width=800, height=700)
  plot(dates,logdiff_to_orig(fitted(x),s2$adjClose[1]),type="l",xlab="Date",ylab="Price",main=paste(TICKER," simulation ",i,sep=""))
  dev.off()
}


