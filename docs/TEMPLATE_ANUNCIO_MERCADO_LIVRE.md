# 🛠️ GUIA DE ESCRITA & TEMPLATE DE ALTA CONVERSÃO — AUTO PEÇAS
## Padrão de Comunicação Especialista (Voz Autêntica de Balcão de Autopeças + SEO Mercado Livre)

Este padrão foi desenvolvido para transformar anúncios técnicos em vendas reais no Mercado Livre. A escrita abandona jargões corporativos genéricos e adota o tom de um **especialista experiente em autopeças**: direto, transparente, prestativo e focado em resolver a dor do motorista ou do mecânico (garantia de que a peça vai servir perfeitamente sem dor de cabeça).

---

### 🎯 1. DIRETRIZES DE ESTILO & TOM DE VOZ

1. **Tom de Especialista de Balcão:**
   - Comunicação clara, honesta e técnica.
   - Explicações práticas sobre como identificar a peça correta no carro (ex: conferir número de pinos, se tem limpador traseiro, tipo de motor).
   - Menos "marketing genérico e artificial" e mais **informação técnica útil e confiável**.
2. **Emojis Temáticos e Moderados (Mecânica e Autopeças):**
   - 🔩 (Fixação / Componente)
   - 🚗 (Aplicação / Veículos)
   - ⚙️ (Mecânica / Engrenagens)
   - 🔌 (Elétrica / Conectores e Pinos)
   - 🛠️ (Instalação / Dicas da Oficina)
   - ⚠️ (Atenção / Variações de Modelo)
   - 📦 (Envio / Embalagem)
   - 🛡️ (Garantia / Nota Fiscal)
   - 💡 (Dica Técnica)
   - ❓ (Dúvidas Frequentes)
3. **Títulos SEO para o Algoritmo do Mercado Livre:**
   - **Opção 1 (SEO Principal):** Limite estrito de **máximo 60 caracteres** (ideal para o app mobile do Mercado Livre).  
     *Estrutura:* `[Nome da Peça] + [Aplicação / Modelo] + [Ano/Detalhe] + [Marca/Código]`
   - **Opção 2 (Foco em Montadora e Código Original OEM):** Para compradores que buscam pelo número gravado na carcaça.
   - **Opção 3 (Long-Tail / Busca Específica):** Foco em versões e variações de motorização.

---

### 📐 2. ESTRUTURA DO TEMPLATE OFICIAL DE ANÚNCIO

Cada arquivo em `docs/anuncios/ANUNCIO_[ID]_[SLUG].md` deve conter:

```markdown
---
id: [ID_NUM]
sku_master: "[SKU_MASTER]"
titulo_ml_principal: "[TITULO_SEO_MAX_60_CHARS]"
titulo_ml_alternativo_oem: "[TITULO_OEM]"
titulo_ml_long_tail: "[TITULO_LONG_TAIL]"
categoria_nivel_1: "[CATEGORIA_1]"
categoria_nivel_2: "[CATEGORIA_2]"
preco_venda_brl: [VALOR]
comissao_10_pct_brl: [COMISSAO_10%]
quantidade_estoque: 1
garantia_meses: [GARANTIA]
status_anuncio: "PRONTO_PARA_PUBLICACAO"
---

# 📦 ANÚNCIO: [NOME_COMERCIAL_BASE]

> **SKU:** `[SKU_MASTER]` | **Código Fabricante:** `[CODIGO_FABRICANTE]` | **Estoque Físico:** `1 Unidade` | **Disponível para Envio Imediato**

---

### 🏷️ Sugestões de Título para o Mercado Livre

1. **Opção 1 (SEO Principal - Máximo 60 Caracteres):**
   `[TITULO_1]`  
   *📏 Comprimento: XX caracteres (perfeito para a busca no app mobile do ML)*

2. **Opção 2 (Busca por Código Original OEM / Montadora):**
   `[TITULO_2]`

3. **Opção 3 (Busca Específica / Long-Tail):**
   `[TITULO_3]`

---

## 📝 Descrição do Produto (Pronta para o Mercado Livre)

---

### 🔩 [NOME_DA_PECA] — [MARCA_FABRICANTE] (CÓDIGO: [CODIGO_FABRICANTE])

Seja bem-vindo à nossa loja de autopeças! Se você precisa substituir [FUNCAO_DA_PECA] no seu carro com a tranquilidade de colocar uma peça de **qualidade comprovada, encaixe original e durabilidade real**, este é o componente exato.

Fabricado pela **[MARCA_FABRICANTE]**, este item segue rigorosamente os padrões das linhas de montagem, garantindo contatos elétricos precisos, resistência ao calor do motor e perfeito alinhamento no veículo.

---

### 🚗 VEÍCULOS COMPATÍVEIS (TABELA DE APLICAÇÃO)

Confira se o modelo e ano do seu carro estão listados abaixo:

| Montadora | Modelo | Versão / Detalhe | Motorização | Combustível | Anos de Aplicação |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [TABELA_COMPATIBILIDADE] |

---

### ⚠️ ATENÇÃO: NÃO COMPRE ANTES DE CONFERIR ESTES DETALHES!
[ALERTAS_CRITICOS_DE_COMPATIBILIDADE]

> 💡 **Dica do Especialista:** *Na dúvida sobre a versão do seu carro, não arrisque! Deixe uma pergunta abaixo informando o ano, motor, se tem ar-condicionado ou se tem opcionais específicos. Nossa equipe responde na hora para você comprar com 100% de certeza.*

---

### ⚙️ ESPECIFICAÇÕES TÉCNICAS & CÓDIGOS

- 🏷️ **Fabricante:** **[MARCA_FABRICANTE]**
- 🔢 **Código da Peça:** `[CODIGO_FABRICANTE]`
- 🏛️ **Códigos Originais da Montadora (OEM):** `[LISTA_OEM]`
- 🔄 **Códigos Similares / Equivalentes:** `[LISTA_CRUZADOS]`
- 📍 **Local de Instalação:** [POSICAO]
- 🔌 **Conectores / Vias:** [PINAGEM_E_CONEXAO]
- 🛡️ **Garantia:** **[GARANTIA_MESES] meses** de garantia
- 📦 **O que vem na caixa:** 1x [NOME_DA_PECA] lacrada de fábrica

---

### 🛡️ POR QUE COMPRAR COM A GENTE?

- 📦 **Estoque Próprio & Envio Imediato:** Produto em mãos, despachado em até 24h úteis pelo Mercado Envios.
- 🧾 **Nota Fiscal em Todos os Pedidos:** Transparência e procedência garantida para CPF e CNPJ.
- 🔒 **Compra 100% Protegida:** Pagamento seguro via Mercado Pago.
- 📞 **Suporte Pré e Pós-Venda:** Atendimento humanizado por quem realmente entende de autopeças.

---

### 🛠️ DICAS DE INSTALAÇÃO & CUIDADOS

1. **Desconecte a bateria:** Antes de mexer na parte elétrica do carro, solte o polo negativo da bateria para evitar queima de fusíveis ou módulos.
2. **Cuidado com as travas:** Encaixe os plugues com calma nas travas plásticas originais sem puxar a fiação.
3. **Mão de obra:** Recomendamos a instalação por um autoelétrico ou mecânico de confiança para garantir o perfeito funcionamento.

---

### ❓ DÚVIDAS FREQUENTES

**1. O produto é novo?**  
*Sim! Só trabalhamos com produtos 100% novos, lacrados na caixa e direto do fabricante.*

**2. Tem pronta entrega?**  
*Sim, temos estoque físico real pronto para envio no mesmo dia ou no próximo dia útil.*

**3. Emite Nota Fiscal?**  
*Sim! Todos os nossos pedidos acompanham Nota Fiscal eletrônica em nome do comprador.*

**4. Como confirmo se serve no meu carro?**  
*Basta conferir a tabela acima ou nos mandar uma pergunta com os dados do seu veículo antes de finalizar a compra.*

---

### 🛒 GARANTA A SUA PEÇA AGORA!
*Clique em **Comprar Agora** e receba no conforto da sua oficina ou residência com a rapidez e segurança do Mercado Livre!*
```
