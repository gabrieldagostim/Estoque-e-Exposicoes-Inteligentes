<h2>Seja Bem-vindo ao repositório "Estoque e Exposições Inteligentes"</h2>

<p> Esse projeto exemplifica como a análise de dados pode ser aplicada para otimizar estoques de exposições extras e promocionais em na Bistek Supermercados, que hoje é composta por 22 lojas. Com uma variedade de móveis e um universo de mais de 20.000 Skus ativos, a necessidade de distribuição eficiente é desafiadora. 
</p>

<p>Neste repositório, você encontrará um script em Python que detalha nossas estratégias e soluções para lidar com esse desafio. Demonstramos como analisar dados complexos pode evitar o excesso de produtos nas lojas, garantindo que o necessário esteja sempre disponível.
</p>

<p>Nosso foco está na eficiência operacional e na melhoria da experiência do cliente. O projeto explora como a análise inteligente de dados pode ser uma ferramenta poderosa no setor de varejo, oferecendo benefícios tangíveis.
</p>

<p>
  Sinta-se à vontade para explorar o código e as análises apresentadas aqui. Este repositório, serve como um exemplo do meu compromisso com a aplicação prática da análise de dados em contextos comerciais desafiadores.
</p>


<h4>Alguns conceitos importantes antes de adentrarmos na metodologia utilizada: </h4>

<h2>CAPACIDADE DO MÓVEL </h2>
<p>A capacidade do móvel é calculada com a medida do produto versus a medida do móvel em si ( ilha, pg e pe) e com parâmetros de exposição do produto que são variáveis, a fim de fornecer flexibilidade do produto e ajustar o estoque conforme necessário.
</p>



<p>as variáveis de capacidade são: </p>

<p>Capacidade área : Quantidade de produtos que cabem dentro da posição (Calculado na área produto x posição pelas medidas)</p>

<p>Empilhamento: Quantidade de vezes que o produto é empilhado na posição (usuário altera) 
</p>

<p>% Preenchimento: Percentual de preenchimento do produto na localização por loja (usuário altera)</p>

<h2>MÓVEIS</h2>

<p>ILHA - Móvel localizado no meio do corredor central e entrada da loja</p>

![ilha](https://github.com/gabrieldagostim/Estoque-e-Exposicoes-Inteligentes/assets/105657571/36891d72-d446-4de4-bf46-56d4d08ff552)


<p>PG - Ponta de gôndola, localizado nas pontas das gondolas nas lojas  </p>
<p> PE - Ponta extra, localizado a lateral da Ponta de Gondôla </p>

![ponta-de-gondola-colgate-01](https://github.com/gabrieldagostim/Estoque-e-Exposicoes-Inteligentes/assets/105657571/830fcd38-af47-4f3a-9f2a-d87db10cffcb)


<p>Cada tipo de móvel possui uma capacidade cadastrada por produto x loja, ou seja, em um universo de 20.000 sku x 22 lojas = 440.000 cadastros </p>


<h2>O QUE É CONSIDERADO EXCESSO DE PRODUTOS NESTA ANÁLISE?</h2>

<p>Foi considerado excesso de produtos onde a necessidade de produto para o ponto extra, excede a venda de 30 dias passados do produto na loja mapeada. (o que aumenta os dias de estoque do produto na loja, um KPI muito importante para o varejo)</p>

<h2>Como funciona o Algoritmo?</h2>

<p>Utilizamos bases de dados extraídos de relatórios disponibilizados pela empresa (via intranet) </p>

<p>as bases são nomeadas como:</p>

<h2> cadastro_usuario_abastecimento </h2>

<p>Correlaciona departamento ao analista responsável por manter o cadastro das exposições do produto por tipo de móvel ( utilizado na base exp ) </p>

<h2>exp</h2>

<p>Contém dados do Sku x Loja por tipo de móvel( ILHA, PG e PE) nas  lojas onde o produto não tem nenhum bloqueio</p>

<h2>Linkker</h2>

<p>Contém os dados dos Skus mapeados x móvel e tipo de móvel por loja onde é mapeado o produto, entre outras informações que são limpas e tratadas no código, automatizando o processo ( retirando informações preenchidas de forma erradas pelo comprador/gerente comercial do departamento)</p>

<h2>mix_total </h2>

<p>
  Contém informações do produto das mais variadas, utilizamos para categorizar os produtos atribuir comprador responsável entre outras utilidades
</p>

<h2>O output do script</h2>
<h3>3 relatórios em planilha excel:</h3>

<h2> Relatorio_itens_sem_expositor_cadastrado</h2>
<p>Relatório para o Abastecimento, Primeiro relatório, que contém os itens que foram mapeados pela equipe comercial, porém não temos cadastrados as informações de empilhamento e de reposição.</p>

<p>Separei po analista responsável pelo departamento para que o mesmo já faça o cadastro antes da análise de excesso ( na fórmula precisa que esta informação esteja previamente cadastrada, caso não desqualifica o item para envio para exposição (entra na regra de cadastro inválido))</p>

<p>Após cadastrado informações de expositores baixo as bases novamentes e passo os seguintes relatórios
</p>
<h2>Relatório_comercial</h2>
<p>Relatório enviado para o comercial separados por abas com nome do comprador responsável pelos produtos contidos nele, contém os produtos que irão excesso para as lojas se continuarem mapeados as ações geralmente são: Retirar/trocar itens mapeados na posição ou solicitar a equipe de abastecimento alterar as variáveis
</p>

<h2>Relatório_comercial_agrupado</h2>
<p>Desenvolvi esse relatório para consulta rápida para verificar quando precisa consultar alguma informação e consultar se a etapa de cálculo está correta </p>

<h2>Pergunta de negócio:</h2>
<h1>O item mapeado na posição x loja x móvel vai gerar excesso na loja?</h1>

<p>Quanto ao cálculo para responder a pergunta de negócio:
</p>

<div style="font-size: 20px;"> 
        <span style="vertical-align: middle;">v30 / (</span>
        <span style="border-top: 1px solid #000; display: inline-block; width: 100px; text-align: center;">Soma da venda dos itens mapeados</span>
        <span style="vertical-align: middle;">) * Capacidade Total do Expositor = Qtd Exp. Temp</span>
</div>
<p>onde:</p>
<p>v30 -> Venda de 30 dias anteriores do produto na loja
</p>
<p>Soma da venda dos itens mapeados -> Soma da venda de 30 dias anteriores dos produtos na posição mapeada na planilha linkker excluindo os itens com saldo no Centro de Distribuição zerados, e cadastros incorretos</p>
<p>Capacidade Total do Expositor -> Capacidade do item x loja x tipo de móvel após passar pelo cadastro do usuário:
</p>
<p>Fórmula: 
Capacidade Total Prod.* % Preenchimento * Empilhamento = Capacidade Total do Expositor</p>
<p>Qtd Exp. Temp -> Quantidade que irá solicitar por produto para preenchimento daquela posição em uma loja.</p>
<p>Agora que sabemos a quantidade que vamos enviar do produto na posição, como a logística da loja não funciona por item e sim por loja
</p>
<p>precisamos somar a Qtd Exp. Temp do produto na loja que estamos analisando, e temos o adicionei uma coluna no DataFrame para armazenar esse resultado para que possamos analisar com a venda de 30 dias e considerar excesso ou não.</p>

<p>Obrigado por acompanhar até aqui, estou estudando para automatizar a extração do relatório na intranet com Web Scraping usando a biblioteca Playwright, de automação de testes mas que serve ao quesitos de extração de dados em sites sem precisar instalar e setar o navegador utilizado.
</p>
