# Documentação de Uso

## Como Funciona?

O `antigravity_rpm_builder.py` é um wrapper inteligente em Python. Em vez de raspar (scrape) a página web estaticamente (o que pode quebrar facilmente quando a UI muda), o script aciona a inteligência do agente através do CLI `agy`.

1. O script invoca `agy -p "<prompt>"` para pedir a localização exata do arquivo `.tar.gz` de lançamento mais recente.
2. Faz o download do **Antigravity IDE** e do **Antigravity Agents**.
3. Move os tarballs para a pasta correta (`~/rpmbuild/SOURCES`).
4. Cria dinamicamente um arquivo `.spec` com os caminhos corretos de `%prep` e `%install`.
5. Aciona o comando nativo `rpmbuild -bb` para criar o binário final no seu diretório `~/rpmbuild/RPMS/x86_64/`.

## Instalação Rápida

1. Instale as dependências de sistema (Exemplo no Fedora/RHEL):
   ```bash
   sudo dnf install -y rpm-build rpmdevtools
   ```

2. Certifique-se de que o CLI `agy` esteja acessível no seu `$PATH`.

3. Execute o script:
   ```bash
   chmod +x antigravity_rpm_builder.py
   ./antigravity_rpm_builder.py
   ```

4. Após a mensagem de sucesso, instale o pacote:
   ```bash
   sudo rpm -Uvh ~/rpmbuild/RPMS/x86_64/antigravity-suite-*.rpm
   ```

## Solução de Problemas

- **Erro `agy: command not found`**: O script depende do Antigravity CLI para resolver as URLs com Inteligência Artificial. Certifique-se de que o IDE do Antigravity está instalado e os binários estão no `$PATH`.
- **Falha de Autenticação**: Como o `agy` herda a autenticação do seu ambiente, certifique-se de que sua assinatura (IDE) está ativa. O fallback de emergência usará links estáticos salvos no script caso o agente falhe.
