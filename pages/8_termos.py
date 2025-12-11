import streamlit as st

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="Curso",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* Esconde o link da página de Cadastro (Usando a capitalização 'CADASTRO') */
    [data-testid="stSidebarNav"] a[href*="CADASTRO"] {
        display: none !important;
    }

    /* Esconde o link da página de Recuperação de Senha (Supondo que o href contenha 'rec_senha') */
    [data-testid="stSidebarNav"] a[href*="rec_senha"] {
        display: none !important;
    }

    /* FIX DEFINITIVO: Esconde a página Home (Arquivo principal/raiz). 
       Este seletor mira o PRIMEIRO item da lista de navegação (li:first-child), 
       o que é garantido para funcionar na Home. */
    [data-testid="stSidebarNav"] li:first-child a { 
        display: none !important; 
    }

    /* Esconde o link da página de Pagamento (Usando a capitalização 'Pagamento') */
    [data-testid="stSidebarNav"] a[href*="Pagamento"] {
        display: none !important;
    }
    
    /* Esconde o link da página de termos (Usando a capitalização 'Termos') */
    [data-testid="stSidebarNav"] a[href*="termos"] {
        display: none !important;
    }
    /* Esconde o link da página de Politica (Usando a capitalização 'politica') */
    [data-testid="stSidebarNav"] a[href*="politica"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Variáveis para substituição ---
NOME_EMPRESA = "Autoescola em video"
EMAIL_CONTATO = "autoescolaemvideo@gmail.com"
JURISDICAO = "República Federativa do Brasil"

# --- Conteúdo da Política de Privacidade (em formato Markdown) ---
politica_privacidade_markdown = f"""
# Política de Privacidade

A sua privacidade é importante para nós. É política da **Autoescola em video** respeitar a sua privacidade em relação a qualquer informação sua que possamos coletar no site **Autoescola em video** (`https://autoescolaemvideo.onrender.com`), e outros sites que possuímos e operamos.

Solicitamos informações pessoais apenas quando realmente precisamos delas para lhe fornecer um serviço. Fazemo-lo por meios justos e legais, com o seu conhecimento e consentimento. Também informamos por que estamos coletando e como será usado.

Além disso, nós coletamos o endereço IP utilizado para conectar o seu computador à Internet; dados de login; endereço de email; senha; informações do computador e internet e histórico de compra, geolocalização e movimento do mouse nas telas de nosso site, durante o uso do mesmo. Nós poderemos utilizar ferramentas para medir e coletar informações de navegação, incluindo o tempo de resposta das páginas, tempo total da visita em determinadas páginas, informações de interação com página e os métodos utilizados para deixar a página. Nós também coletamos informações de identificação pessoal (incluindo nome, email, senha, meios de comunicação); detalhes de pagamento (incluindo informações de cartão de crédito), comentários, feedback, recomendações e perfil pessoal.

Apenas retemos as informações coletadas pelo tempo necessário para fornecer o serviço solicitado. Quando armazenamos dados, os protegemos dentro de meios comercialmente aceitáveis para evitar perdas e roubos, bem como acesso, divulgação, cópia, uso ou modificação não autorizados.

Coletamos essas Informações Pessoais e Não Pessoais com as seguintes finalidades:

* Para prestar e operar os Serviços;
* Para prestar aos nossos Usuários assistência e suporte técnico contínuos ao cliente;
* Para poder entrar em contato com nossos Visitantes e Usuários com avisos gerais ou personalizados relacionados ao serviço e mensagens promocionais;
* Para criar dados estatísticos agregados e outras informações não pessoais agregadas e/ou inferidas, que podem ser usadas por nós ou por nossos parceiros comerciais para prestar e melhorar nossos respectivos serviços;
* Para cumprir quaisquer leis e regulamentos aplicáveis.

Não compartilhamos informações de identificação pessoal publicamente ou com terceiros, exceto quando exigido por lei.

O nosso site pode ter links para sites externos que não são operados por nós. Esteja ciente de que não temos controle sobre o conteúdo e práticas desses sites e não podemos aceitar responsabilidade por suas respectivas políticas de privacidade.

Você é livre para recusar a nossa solicitação de informações pessoais, entendendo que talvez não possamos fornecer alguns dos serviços desejados.

O uso continuado de nosso site será considerado como aceitação de nossas práticas em torno de privacidade e informações pessoais. Se você tiver alguma dúvida sobre como lidamos com dados do usuário e informações pessoais, entre em contacto conosco.

Nós poderemos entrar em contato para notificá-lo a respeito de sua conta, para ajudá-lo a resolver alguma questão relacionada a sua conta, para solucionar uma disputa de pagamento, para coletar taxas ou dívidas, para pesquisas ou questionários, para novidades sobre nossa empresa ou para qualquer outro motivo que seja necessário revisar o nosso contrato, de acordo com as leis locais. Para isso, poderemos entrar em contato via email, telefone, mensagens de texto e correio.

---

## Política de Cookies Autoescola em video

### O que são cookies?

Como é prática comum em quase todos os sites profissionais, este site usa cookies, que são pequenos arquivos baixados no seu computador, para melhorar sua experiência. Esta página descreve quais informações eles coletam, como as usamos e por que às vezes precisamos armazenar esses cookies. Também compartilharemos como você pode impedir que esses cookies sejam armazenados, no entanto, isso pode fazer o downgrade ou ‘quebrar’ certos elementos da funcionalidade do site.

### Como usamos os cookies?

Utilizamos cookies por vários motivos, detalhados abaixo. Infelizmente, na maioria dos casos, não existem opções padrão do setor para desativar os cookies sem desativar completamente a funcionalidade e os recursos que eles adicionam a este site. É recomendável que você deixe todos os cookies se não tiver certeza se precisa ou não deles, caso sejam usados para fornecer um serviço que você usa.

### Desativar cookies

Você pode impedir a configuração de cookies ajustando as configurações do seu navegador (consulte a Ajuda do navegador para saber como fazer isso). Esteja ciente de que a desativação de cookies afetará a funcionalidade deste e de muitos outros sites que você visita. A desativação de cookies geralmente resultará na desativação de determinadas funcionalidades e recursos deste site. Portanto, é recomendável que você não desative os cookies.

### Cookies que definimos

* **Cookies relacionados à conta:** Se você criar uma conta conosco, usaremos cookies para o gerenciamento do processo de inscrição e administração geral. Esses cookies geralmente serão excluídos quando você sair do sistema, porém, em alguns casos, eles poderão permanecer posteriormente para lembrar as preferências do seu site ao sair.
* **Cookies relacionados ao login:** Utilizamos cookies quando você está logado, para que possamos lembrar dessa ação. Isso evita que você precise fazer login sempre que visitar uma nova página. Esses cookies são normalmente removidos ou limpos quando você efetua logout para garantir que você possa acessar apenas a recursos e áreas restritas ao efetuar login.
* **Cookies relacionados a boletins por e-mail:** Este site oferece serviços de assinatura de boletim informativo ou e-mail e os cookies podem ser usados para lembrar se você já está registrado e se deve mostrar determinadas notificações válidas apenas para usuários inscritos ou não inscritos.
* **Pedidos processando cookies relacionados:** Este site oferece facilidades de comércio eletrônico ou pagamento e alguns cookies são essenciais para garantir que seu pedido seja lembrado entre as páginas, para que possamos processá-lo adequadamente.
* **Cookies relacionados a pesquisas:** Periodicamente, oferecemos pesquisas e questionários para fornecer informações interessantes, ferramentas úteis ou para entender nossa base de usuários com mais precisão. Essas pesquisas podem usar cookies para lembrar quem já participou numa pesquisa ou para fornecer resultados precisos após a alteração das páginas.
* **Cookies relacionados a formulários:** Quando você envia dados por meio de um formulário como os encontrados nas páginas de contacto ou nos formulários de comentários, os cookies podem ser configurados para lembrar os detalhes do usuário para correspondência futura.
* **Cookies de preferências do site:** Para proporcionar uma ótima experiência neste site, fornecemos a funcionalidade para definir suas preferências de como esse site é executado quando você o usa. Para lembrar suas preferências, precisamos definir cookies para que essas informações possam ser chamadas sempre que você interagir com uma página for afetada por suas preferências.

### Cookies de Terceiros

Em alguns casos especiais, também usamos cookies fornecidos por terceiros confiáveis. A seção a seguir detalha quais cookies de terceiros você pode encontrar através deste site.

* Este site usa o Google Analytics, que é uma das soluções de análise mais difundidas e confiáveis da Web, para nos ajudar a entender como você usa o site e como podemos melhorar sua experiência. Esses cookies podem rastrear itens como quanto tempo você gasta no site e as páginas visitadas, para que possamos continuar produzindo conteúdo atraente.
    * *Para mais informações sobre cookies do Google Analytics, consulte a página oficial do Google Analytics.*
* As análises de terceiros são usadas para rastrear e medir o uso deste site, para que possamos continuar produzindo conteúdo atrativo. Esses cookies podem rastrear itens como o tempo que você passa no site ou as páginas visitadas, o que nos ajuda a entender como podemos melhorar o site para você.
* Periodicamente, testamos novos recursos e fazemos alterações sutis na maneira como o site se apresenta. Quando ainda estamos testando novos recursos, esses cookies podem ser usados para garantir que você receba uma experiência consistente enquanto estiver no site, enquanto entendemos quais otimizações os nossos usuários mais apreciam.
* À medida que vendemos produtos, é importante entendermos as estatísticas sobre quantos visitantes de nosso site realmente compram e, portanto, esse é o tipo de dados que esses cookies rastrearão. Isso é importante para você, pois significa que podemos fazer previsões de negócios com precisão que nos permitem analisar nossos custos de publicidade e produtos para garantir o melhor preço possível.
* O serviço Google AdSense que usamos para veicular publicidade usa um cookie DoubleClick para veicular anúncios mais relevantes em toda a Web e limitar o número de vezes que um determinado anúncio é exibido para você.
    * *Para mais informações sobre o Google AdSense, consulte as FAQs oficiais sobre privacidade do Google AdSense.*
* Vários parceiros anunciam em nosso nome e os cookies de rastreamento de afiliados simplesmente nos permitem ver se nossos clientes acessaram o site através de um dos sites de nossos parceiros, para que possamos creditá-los adequadamente e, quando aplicável, permitir que nossos parceiros afiliados ofereçam qualquer promoção que pode fornecê-lo para fazer uma compra.

---

## Compromisso do Usuário

O usuário se compromete a fazer uso adequado dos conteúdos e da informação que a **Autoescola em video** oferece no site e com caráter enunciativo, mas não limitativo:

A) Não se envolver em atividades que sejam ilegais ou contrárias à boa fé a à ordem pública;
B) Não difundir propaganda ou conteúdo de natureza racista, xenofóbica, apostas online (ex.: ), jogos de sorte e azar, qualquer tipo de pornografia ilegal, de apologia ao terrorismo ou contra os direitos humanos;
C) Não causar danos aos sistemas físicos (hardwares) e lógicos (softwares) da **Autoescola em video**, de seus fornecedores ou terceiros, para introduzir ou disseminar vírus informáticos ou quaisquer outros sistemas de hardware ou software que sejam capazes de causar danos anteriormente mencionados.

---

## Mais informações

Esperemos que esteja esclarecido e, como mencionado anteriormente, se houver algo que você não tem certeza se precisa ou não, geralmente é mais seguro deixar os cookies ativados, caso interaja com um dos recursos que você usa em nosso site.

Caso você não queira que mais que seja possível para nós coletar as suas informações pessoais, por favor entre em contato através do e-mail **autoescolaemvideo@gmail.com**.

Nós temos o direito de modificar essa política de privacidade a qualquer momento, portanto consulte regularmente. As alterações serão imediatamente colocadas em prática após a alteração em nosso site. Caso realizemos mudanças referentes aos materiais dessa política, você será notificado para que esteja ciente das informações que coletamos e como as utilizamos.

Esta política é efetiva a partir de **Novembro/2025**.
---
"""

# --- Conteúdo dos Termos de Uso (em formato Markdown) ---
termos_uso_markdown = f"""
# Termos de Serviço

## 1. Termos

Este site pertence e é operado por **CENTRO DE FORMACAO DE CONDUTORES VIDA LTDA 07.752.452/0001-79**. Ao acessar o site **Autoescola em video**, concorda em cumprir estes termos de serviço, todas as leis e regulamentos aplicáveis ​​e concorda que é responsável pelo cumprimento de todas as leis locais aplicáveis. Se você não concordar com algum desses termos, está proibido de usar ou acessar este site. Os materiais contidos neste site são protegidos pelas leis de direitos autorais e marcas comerciais aplicáveis.

## 2. Uso de Licença

O Serviço e todos os materiais nele contidos ou transferidos, incluindo, sem limitação, software, imagens, textos, gráficos, logotipos, patentes, marcas registradas, marcas de serviço, direitos autorais, fotografias, áudio, vídeos, música e todos os Direitos de Propriedade Intelectual relacionados a eles são a propriedade exclusiva de **CENTRO DE FORMACAO DE CONDUTORES VIDA LTDA 07.752.452/0001-79**. Exceto conforme explicitamente fornecido neste documento, nada nestes Termos deverá ser considerado como uma licença em ou sob tais Direitos de Propriedade Intelectual, e você concorda em não vender, licenciar, alugar, modificar, distribuir, copiar, reproduzir, transmitir, exibir publicamente, realizar publicamente, publicar, adaptar, editar ou criar trabalhos derivados.

É concedida permissão para baixar temporariamente uma cópia dos materiais (informações ou software) no site **Autoescola em video**, apenas para visualização transitória pessoal e não comercial. Esta é a concessão de uma licença, não uma transferência de título e, sob esta licença, você não pode:

* Modificar ou copiar os materiais;
* Usar os materiais para qualquer finalidade comercial ou para exibição pública (comercial ou não comercial);
* Tentar descompilar ou fazer engenharia reversa de qualquer software contido no site **Autoescola em video**;
* Remover quaisquer direitos autorais ou outras notações de propriedade dos materiais; ou
* Transferir os materiais para outra pessoa ou ‘espelhar’ os materiais em qualquer outro servidor.

Podemos rescindir ou suspender permanentemente ou temporariamente seu acesso ao serviço sem aviso prévio e responsabilidade por qualquer motivo, inclusive se, em nossa única e exclusiva determinação, você violar qualquer disposição destes Termos ou qualquer lei ou regulamentação aplicável. Você pode interromper o uso e solicitar o cancelamento da sua conta e / ou de qualquer serviço a qualquer momento. Não obstante qualquer disposição em contrário no que diz respeito a assinaturas automaticamente renovadas de serviços pagos, tais assinaturas serão descontinuadas somente após o término do respectivo período para o qual você já efetuou pagamento. Ao encerrar a visualização desses materiais ou após o término desta licença, você deve apagar todos os materiais baixados em sua posse, seja em formato eletrónico ou impresso.

## 3. Isenção de responsabilidade

Os materiais no site da **Autoescola em video** são fornecidos ‘como estão’. **Autoescola em video** não oferece garantias, expressas ou implícitas, e, por este meio, isenta e nega todas as outras garantias, incluindo, sem limitação, garantias implícitas ou condições de comercialização, adequação a um fim específico ou não violação de propriedade intelectual ou outra violação de direitos.

Além disso, a **Autoescola em video** não garante ou faz qualquer representação relativa à precisão, aos resultados prováveis ​​ou à confiabilidade do uso dos materiais em seu site ou de outra forma relacionado a esses materiais ou em sites vinculados a este site.

## 4. Limitações

Em nenhum caso a **Autoescola em video** ou seus fornecedores serão responsáveis ​​por quaisquer danos (incluindo, sem limitação, danos por perda de dados ou lucro ou devido a interrupção dos negócios) decorrentes do uso ou da incapacidade de usar os materiais em **Autoescola em video**, mesmo que **Autoescola em video** ou um representante autorizado da **Autoescola em video** tenha sido notificado oralmente ou por escrito da possibilidade de tais danos. Como algumas jurisdições não permitem limitações em garantias implícitas, ou limitações de responsabilidade por danos consequentes ou incidentais, essas limitações podem não se aplicar a você.

## 5. Indenização

Você concorda em indenizar e isentar **CENTRO DE FORMACAO DE CONDUTORES VIDA LTDA 07.752.452/0001-79** de quaisquer demandas, perdas, responsabilidades, reclamações ou despesas (incluindo honorários advocatícios), feitas contra eles por qualquer terceiro devido a, ou decorrentes de, ou em conexão com o uso do site ou qualquer um dos serviços oferecidos no site.

## 6. Precisão dos materiais

Os materiais exibidos no site da **Autoescola em video** podem incluir erros técnicos, tipográficos ou fotográficos. **Autoescola em video** não garante que qualquer material em seu site seja preciso, completo ou atual. **Autoescola em video** pode fazer alterações nos materiais contidos em seu site a qualquer momento, sem aviso prévio. No entanto, **Autoescola em video** não se compromete a atualizar os materiais.

## 7. Links

**Autoescola em video** não analisou todos os sites vinculados ao seu site e não é responsável pelo conteúdo de nenhum site vinculado. A inclusão de qualquer link não implica endosso por **Autoescola em video** do site. O uso de qualquer site vinculado é por conta e risco do usuário.

## 8. Compras

Ao comprar um item, você concorda que:

* É responsável por ler a listagem completa do item antes de assumir o compromisso de comprá-lo.
* Aceita um contrato juridicamente vinculativo para comprar um item quando se compromete a comprar um item e você conclui o processo de pagamento de check-out.

Os preços que cobramos pelos nossos serviços / produtos estão listados no site. Reservamo-nos o direito de alterar nossos preços de produtos exibidos a qualquer momento e corrigir erros de precificação que possam ocorrer inadvertidamente. Informações adicionais sobre preços e impostos sobre vendas estão disponíveis na página de pagamentos.

Podemos, sem aviso prévio, alterar os serviços; deixar de fornecer os serviços ou quaisquer recursos dos serviços que oferecemos; ou criar limites para os serviços. Podemos rescindir ou suspender, permanentemente ou temporariamente, o acesso aos serviços sem aviso prévio e responsabilidade por qualquer motivo ou sem motivo.

## Modificações

Reservamo-nos o direito de modificar estes termos de tempos em tempos, a nosso exclusivo critério. Portanto, você deve revisar essas páginas periodicamente. Quando alterarmos os Termos de maneira material, você será notificado. Seu uso continuado do Site ou de nosso serviço após qualquer alteração constitui sua aceitação dos novos Termos. Se você não concordar com algum destes termos ou qualquer versão futura dos Termos, não use ou acesse (ou continue a acessar) o site ou o serviço.

## E-mails promocionais e conteúdo

Você concorda em receber de tempos em tempos mensagens promocionais e materiais por correio, e-mail ou qualquer outro formulário de contato que você possa nos fornecer (incluindo seu número de telefone para chamadas ou mensagens de texto). Se você não deseja receber esses materiais promocionais ou avisos – por favor, basta nos notificar a qualquer momento.

## Lei aplicável

Estes Termos, os direitos e recursos aqui previstos, e todas e quaisquer reclamações e disputas relacionadas a ele e / ou aos serviços, serão regidos, interpretados e aplicados em todos os aspectos única e exclusivamente de acordo com as leis internas da República Federativa do Brasil, sem respeito aos seus conflitos de princípios legais. Todas e quaisquer reclamações e disputas serão apresentadas, e você consente que elas sejam decididas exclusivamente por um tribunal de jurisdição competente localizado em Porto Alegre, Rio Grande do Sul, Brasil. A aplicação da Convenção das Nações Unidas de Contratos para a Venda Internacional de Bens é expressamente excluída.
---
"""

# -----------------------------------------------------
# --- Estrutura do Streamlit ---
# -----------------------------------------------------

st.title("Documentos Legais da Plataforma")

# st.info("**ATENÇÃO:** Lembre-se de **substituir** os placeholders `[Nome da Sua Empresa/Plataforma]`, `[Seu Email de Contato]` e `[Jurisdição]` no código-fonte por suas informações reais e consultar um **advogado**.")

# Adiciona um seletor para que o usuário escolha qual documento quer ver
opcao = st.selectbox(
    "Selecione o documento que deseja visualizar:",
    ("Termos de Uso", "Política de Privacidade")
)

st.write("---")

if opcao == "Política de Privacidade":
    # Exibe o conteúdo da Política de Privacidade usando Markdown
    st.markdown(politica_privacidade_markdown, unsafe_allow_html=False)
elif opcao == "Termos de Uso":
    # Exibe o conteúdo dos Termos de Uso usando Markdown
    st.markdown(termos_uso_markdown, unsafe_allow_html=False)
