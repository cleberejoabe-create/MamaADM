# 🍔 Lanchonete V2

Sistema de gestão para lanchonete feito em Python, Flask e SQLite.

## Recursos

- Dashboard operacional
- Login de usuário
- Gerenciamento de usuários (administrador)
- Perfis de administrador e funcionário
- Alteração de usuário e senha pelo próprio site
- Senhas armazenadas com hash seguro
- Cadastro de produtos e ingredientes
- Estoque mínimo e alerta
- Entradas e saídas de estoque
- Ficha técnica de produtos
- Baixa automática de ingredientes ao vender produtos com ficha técnica
- Registro de vendas
- Formas de pagamento
- Cadastro de fornecedores
- Registro de compras com entrada automática no estoque
- Controle de caixa
- Relatório dos produtos mais vendidos nos últimos 30 dias
- Interface responsiva para computador e celular

## Instalação

Requer Python 3.10+.

No Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Depois abra:

http://127.0.0.1:5000

## Login inicial

Usuário: `admin`

Senha: `admin123`

Após entrar, use **Meu perfil > Alterar senha** para trocar a senha. Administradores também podem acessar **Usuários** para criar, editar ou excluir contas. Troque também a SECRET_KEY antes de colocar o sistema em produção ou disponibilizá-lo na internet.

## Como usar a ficha técnica

1. Cadastre os ingredientes, por exemplo:
   - Pão
   - Carne 120g
   - Queijo
   - Bacon
   - Molho

2. Cadastre o produto vendido, por exemplo `X-Bacon`, com o preço de venda.

3. Entre em Produtos > Ficha e adicione os ingredientes e suas quantidades.

4. Ao registrar uma venda de X-Bacon, o sistema descontará automaticamente os ingredientes da ficha.

Produtos sem ficha técnica são tratados como itens de estoque vendidos diretamente, como refrigerantes e águas.

## Observação

Esta é uma versão local inicial. Para uso real em vários computadores/celulares, backup automático, emissão fiscal, integração com delivery, impressoras, permissões avançadas e publicação na internet, recomenda-se uma etapa posterior de produção.
