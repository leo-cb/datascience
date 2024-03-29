#########################################################
### BIBLIOTECAS
#########################################################

# pkgTest = function(x)
# {
#   if (!require(x,character.only = TRUE))
#   {
#     install.packages(x,dep=TRUE)
#     if(!require(x,character.only = TRUE)) stop("Package not found")
#   }
# }
# 
# pkgTest("rgl")
# library(rgl)

#########################################################
### FUN��ES AUXILIARES
#########################################################

# calcula custo de solu��o descodificada v
custo = function(v)
{
  n = length(v)
  soma = 0
  
  for (i in 1:(n-1))
    if (v[i] != v[i+1]) # v�rtices diferentes, somar custo
      soma = soma + as.numeric(custos[v[i]+1,v[i+1]+1])
    else # adicionar custo alto caso hajam dois v�rtices iguais consecutivos (solu��o n�o-admiss�vel)
      soma = soma + 9999999999
  
  return(soma)
}
 
# calcula potencial total de solu��o descodificada v
potencial = function(v)
{
  n = length(v)
  soma = 0
  
  for (i in 1:n)
  {
    if (v[i] != 0)
      soma = soma + potenciais[v[i]]
  }
  
  return(soma)
}

# retorna solu��o admiss�vel com maior aptid�o na lista
solucao_melh = function(lista)
{
  max_aptidao = 0
  best_sol = c()
  
  for (i in 1:length(lista))
  {
      sol = descodificador(lista[[i]])
      apt = aptidao(sol)
      
      if (potencial(sol) >= POTENCIAL_MIN && apt > max_aptidao)
      {
        best_sol = sol
        max_aptidao = apt
      }
  }
    
  return(best_sol)
}

# calcula aptid�o m�dia de popula��o de solu��es na var. lista
aptidao_media = function(lista)
{
  aptidoes = c()
  
  for (i in 1:length(lista))
    aptidoes[length(aptidoes)+1] = aptidao(descodificador(lista[[i]]))
  
  return(mean(aptidoes))
}

# calcula aptid�o mediana de popula��o de solu��es na var. lista
aptidao_mediana = function(lista)
{
  aptidoes = c()
  
  for (i in 1:length(lista))
    aptidoes[length(aptidoes)+1] = aptidao(descodificador(lista[[i]]))
  
  return(median(aptidoes))
}

# retorna aptid�o m�xima de popula��o de solu��es na var. lista
aptidao_maxima = function(lista)
{
  aptidoes = c()
  
  for (i in 1:length(lista))
    aptidoes[length(aptidoes)+1] = aptidao(descodificador(lista[[i]]))

  return(max(aptidoes))
}

# conta n�mero de solu��es n�o-admiss�veis numa popula��o de solu��es na var. lista
contar_nadmissiveis = function(lista)
{
  count = 0
  for (i in 1:length(lista))
  {
    if (potencial(descodificador(lista[[i]])) < POTENCIAL_MIN)
      count = count+1
  }
  
  return(count)
}

# descodifica solu��o codificada 'v_codificado', e retorna em forma de permuta��o num vector
descodificador = function(v_codificado)
{
  return(c(0,v_codificado[v_codificado != 0],0))
}

#########################################################
### APTID�O
#########################################################

# calcula aptid�o de solu��o descodificada v
aptidao = function(v)
{
  # calcular componente de penaliza��o
  penalizacao = tam_sol*custos_mediana*(max(potencial(v),POTENCIAL_MIN) - potencial(v))/POTENCIAL_MIN
  
  # retornar aptid�o
  return(1/(custo(v)+penalizacao)^3)
}

#########################################################
### CRUZAMENTO 'ORDER CROSSOVER' (OX)
#########################################################

# retorna lista de filhos gerados a partir de populacao dada, pelo algoritmo de cruzamento OX
cruzamento_ox = function(populacao)
{
  iter = 0
  
  #########################################################
  ### construir roleta enviesada, atribuindo uma probabilidade de escolha a cada elemento da popula��o
  ### para se tornar um progenitor
  #########################################################

  # inicializar vector de probabilidades de escolha
  probs = c()
  
  for (i in 1:length(populacao))
  {
    # guardar elemento i da popula��o em forma de permuta��o
    elemento = descodificador(populacao[[i]])
    
    # obter aptid�o do elemento i da popula��o
    probs[i] = aptidao(elemento)
  }
  
  # normalizar vector para obter probabilidades de escolha
  if (!is.na(sum(probs)) && sum(probs) != 0)
    probs = probs/sum(probs)
  else
    probs = rep(1/length(populacao),length(populacao))

  # gerar progenitores no mesmo n�mero que tamanho da popula��o, com probabilidades retiradas de 'probs' (roleta enviesada)
  progenitores = sample(1:length(populacao),size=length(populacao),replace=TRUE,prob=probs)
  
  # gerar pares de progenitores aleatoriamente
  pares = list()
  
  while (length(pares)<round(length(progenitores)/2))
  {
    u = sample(1:length(progenitores),1)
    v = sample(1:length(progenitores),1)
    
    if (u != v)
      pares[[length(pares)+1]] = c(u,v)
  }

  #########################################################
  ### obter filhos
  #########################################################
  
  progenitores = list()
  filhos = list()
  
  # iterar sobre todos os pares de progenitores
  for (i in 1:length(pares))
  {
    # calcular limites inferior e superior aleatoriamente
    lim = sort(sample(1:tam_sol,2))
    
    # �ndice para usar nas listas de progenitores e filhos
    idc = 2*i-1
    
    # retirar progenitores de par i
    progenitores[[idc]] = populacao[[ pares[[i]][1] ]]
    progenitores[[idc+1]] = populacao[[ pares[[i]][2] ]]
    
    # inicializar lista de filhos
    filhos[[idc]] = rep(0,tam_sol)
    filhos[[idc+1]] = rep(0,tam_sol)
    
    # realizar cruzamento entre os dois progenitores, desde o limite inferior at� ao limite superior,
    # e guardar na lista filhos
    filhos[[idc]][lim[1]:lim[2]] = progenitores[[2]][lim[1]:lim[2]]
    filhos[[idc+1]][lim[1]:lim[2]] = progenitores[[1]][lim[1]:lim[2]]
    
    # calcular antecessor de limite inferior
    if (lim[1] == 1)
      lim_ant = tam_sol
    else
      lim_ant = lim[1]-1
    
    # calcular sucessor de limite superior
    if (lim[2] == tam_sol)
      lim_post = 1
    else
      lim_post = lim[2]+1
    
    # iterar sobre dois elementos de progenitores e filhos
    for (j in idc:(idc+1))
    {
      progenitor_ord = c(progenitores[[j]][lim_post:tam_sol],progenitores[[j]][1:lim[2]])
      
      # iterar sobre o elemento que sucede limite superior at� elemento que antecede limite inferior
      for (k in c(lim_post:tam_sol,1:lim_ant))
      {
        # iterar sobre elementos de progenitores, come�ando no sucessor de limite superior
        for (w in c(k:tam_sol,1:lim[2]))
        {
          # se filho n�o contiver elemento de progenitor da posi��o w, ou se este elemento for 0, atribuir elemento a filho na posi��o w
          if ( !(progenitores[[j]][w] %in% filhos[[j]]) || progenitores[[j]][w] == 0 )
          {
            filhos[[j]][k] = progenitores[[j]][w]
            break
          }
        }
      }
    }
  }
  
  # retorna lista de filhos
  return(filhos)
}

#########################################################
### ELITISMO
#########################################################

# retorna as (p*100) % solu��es com maior aptid�o na var. lista, por ordem n�o-crescente, em forma de lista
elite = function(lista,p)
{
  aptidoes = c()
  
  # obter aptid�es de todos os elementos de popula��o
  for (i in 1:length(lista))
    aptidoes[i] = aptidao(descodificador(lista[[i]]))
  
  # ordenar aptid�es por ordem n�o-crescente, e obter �ndices ordenados do vector original
  aptos_ord = sort(aptidoes,decreasing=TRUE,index.return=TRUE)$ix
  
  # n�mero m�ximo de elementos para copiar, baseado na propor��o escolhida e tamanho de popula��o
  max_elementos = round(p*length(lista))
  
  ret = list()
  
  # se n�mero de elementos a copiar for maior ou igual a 1, guardar na lista ret as solu��es ordenadas
  if (max_elementos >= 1)
  {
    for (i in 1:max_elementos)
      ret[[i]] = lista[[aptos_ord[i]]]
  }
  
  # retornar lista
  return(ret)
}

#########################################################
### MUTA��O
#########################################################

# para cada solu��o na lista populacao, substitui cada elemento, com probabilidade p,
# por um valor n�o existente na solu��o
mutacao = function(populacao,p)
{
  for (i in 1:length(populacao))
  {
    for (j in 1:length(populacao[[i]]))
    {
      # gerar v.a. uniforme com suporte [0,1]
      u = runif(1,0,1)
      
      # probabilidade p
      if (u <= p)
      {
        # encontrar inteiro n�o existente em solu��o e guardar na var. v
        v = sample.int(tam_sol,1)
        while (v %in% populacao[[i]][-j])
          v = sample.int(tam_sol,1)
          
        # substituir elemento j por v
        populacao[[i]][j] = v
      }
    }
  }
  
  # retorna nova lista de solu��es
  return(populacao)
}

#########################################################
### CARREGAMENTO DE FICHEIRO E INICIALIZA��O DE VARI�VEIS GLOBAIS
#########################################################

# nome de ficheiros
# file_potenciais = "20Pot_aleat_1.txt"
# file_custos = "n20_1.txt"
# 
# # ler ficheiro de potenciais
# data = read.table(file_potenciais,header=T,sep="\t")
# 
# # eliminar primeira linha de potenciais
# data = data[-1,]
# 
# # guardar potencial m�nimo
# POTENCIAL_MIN = as.numeric(data[nrow(data),2])
# 
# # eliminar 2 �ltimas linhas
# data = data[-nrow(data),][-(nrow(data)-1),]
# 
# # guardar potenciais e tamanho de solu��o
# potenciais = as.vector(data[,2])
# tam_sol = length(potenciais)-1
# 
# # ler ficheiro de custos
# data_custos = read.table(file_custos,header=F,sep="\t")
# 
# # guardar matriz de custos
# custos = as.matrix(data_custos)
# colnames(custos) = NULL

potenciais = instancia3_potenciais
custos = instancia3_custos
POTENCIAL_MIN = instancia3_potmin
tam_sol = length(potenciais)-1

# guardar mediana de custos
custos_mediana = median(custos,na.rm=TRUE)

#########################################################
### DEFINI��O DE PAR�METROS
#########################################################

# definir tamanho de popula��o
tam_pop = tam_sol^2

# definir valores para probabilidade de muta��o. Substituir por sequ�ncia com valores entre 0 e 1 para iterar sobre a mesma
mutacao_seq = 0.005 #seq(0.005,0.1,0.003)

# definir valores para propor��o de elitismo. Substituir por sequ�ncia com valores entre 0 e 1 para iterar sobre a mesma
elitismo_seq = 0.30 #seq(0,0.4,0.05)

# definir n�mero de gera��es
n_geracoes = 30

#########################################################
### GERAR POPULA��O
#########################################################

# dataframe para guardar valores de vari�veis a visualizar posteriormente
optimization = setNames(data.frame(matrix(ncol = 4, nrow = 0)), c("pmut", "pelite", "max_apt", "mean_apt"))

# inicializar n�mero de itera��es
iter = 0

# iterar sobre valores de probabilidade de muta��o
for (pmut in mutacao_seq)
{
  # iterar sobre valores de propor��o de elitismo
  for (pelite in elitismo_seq)
  {
    # gerar popula��o inicial
    populacao = list()
    
    for (i in seq(1,tam_pop))
    {
      # com probabilidade 0.7, escolhe elementos de vector aleat�rio com valores inteiros
      # caso contr�rio, elemento assume valor 0
      u = runif(tam_sol,0,1)
      escolher = 1*(u>0.3)
      populacao[[i]] = escolher*sample(1:tam_sol)
      
      # garantir que todas as solu��es iniciais s�o admiss�veis
      while(potencial(populacao[[i]])<POTENCIAL_MIN)
      {
        u = runif(tam_sol,0,1)
        escolher = 1*(u>0.3)
        populacao[[i]] = escolher*sample(1:tam_sol)
      }
    }
    
    # guardar populacao inicial em populacao_nova
    populacao_nova = populacao
  
    # iterar sobre gera��es
    for (i in 1:n_geracoes)
    {
      # obter solu��es elitistas
      pop_elite = elite(populacao_nova,pelite)
      
      # realizar cruzamento em popula��o de solu��es
      populacao_nova = elite(cruzamento_ox(populacao_nova),1-pelite)
      
      # obter solu��es n�o-elitistas, eliminando as (100*pelite) % piores solu��es, em termos de aptid�o
      #pop_regular = elite(populacao_nova,1-pelite)
      
      # realizar muta��o em popula��o de solu��es
      populacao_nova = mutacao(populacao_nova,pmut)
      
      # gerar popula��o final desta gera��o, juntando a popula��o elitista � popula��o n�o-elitista
      populacao_nova = c(pop_elite,populacao_nova)
      
      cat("Gera��o ", i)
    }
    
    # juntar valores a dataframe
    optimization = rbind(optimization,data.frame(pmut=pmut,pelite=pelite,max_apt=aptidao_maxima(populacao_nova),mean_apt=aptidao_media(populacao_nova)))
    
    # actualizar itera��es, e print do seu n�mero
    iter = iter+1
    cat("Itera��o ", iter, "/", length(mutacao_seq)*length(elitismo_seq),"\n")
  }
}

# output

cat("POPULA��O INICIAL\n\tMelhor solu��o: ", solucao_melh(populacao), "\n\tAptid�o m�dia: ", 
    aptidao_media(populacao), "\n\tAptid�o m�xima: ", aptidao_maxima(populacao), "\n\tCusto m�nimo: ", 
    custo(solucao_melh(populacao)), "\n\n")

cat("POPULA��O GERA��O ", n_geracoes, "\n\tMelhor solu��o: ", solucao_melh(populacao_nova), 
    "\n\tAptid�o m�dia: ", aptidao_media(populacao_nova), "\n\tAptid�o m�xima: ", 
    aptidao_maxima(populacao_nova), "\n\tCusto m�nimo: ", custo(solucao_melh(populacao_nova)), 
    "\n\tProbabilidade de muta��o: ", 100*pmut, "%\n\tPropor��o de elitismo: ", 100*pelite, "%\n")


# desenhar gr�ficos se houver mais que um valor escolhido para pmut e pelite
# if (length(mutacao_seq) > 1 && length(elitismo_seq) > 1)
# {
#   # plot de aptid�o m�xima vs pmut vs pelite
#   plot3d(optimization$pelite,optimization$pmut,optimization$max_apt,xlab="Proporcao de elitismo",ylab="Probabilidade de mutacao",zlab="Aptidao Maxima")
#   
#   # plot de m�dia de aptid�o vs pmut vs pelite
#   plot3d(optimization$pelite,optimization$pmut,optimization$mean_apt,xlab="Proporcao de elitismo",ylab="Probabilidade de mutacao",zlab="Aptidao Media")
# }