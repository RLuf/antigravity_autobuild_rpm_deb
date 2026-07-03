#!/usr/bin/env python3
import os
import subprocess
import urllib.request
import shutil
from pathlib import Path
import textwrap
import asyncio

DOWNLOAD_DIR = Path.home() / "Downloads" / "antigravity_rpm_build"
RPMBUILD_DIR = Path.home() / "rpmbuild"
DEBBUILD_DIR = Path.home() / "debbuild" / "antigravity-suite_2.0.0-1_amd64"

def _fallback_urls():
    ide_url = "https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/2.1.1-6123990880747520/linux-x64/Antigravity%20IDE.tar.gz"
    agents_url = "https://storage.googleapis.com/antigravity-public/antigravity-hub/2.2.1-5287492581195776/linux-x64/Antigravity.tar.gz"
    return ide_url, agents_url

def fetch_download_links():
    prompt_ide = (
        "You are an automated release fetcher. We need to find the latest Linux x64 "
        "tarball download link for 'Antigravity IDE'. "
        "The download page is typically https://antigravity.google/download. "
        "Please return ONLY the exact URL for the Linux x64 tarball (.tar.gz), nothing else."
    )
    prompt_agents = (
        "Now, find the latest Linux x64 tarball download link for 'Antigravity Agents/CLI' (Antigravity.tar.gz). "
        "Please return ONLY the exact URL for the .tar.gz, nothing else."
    )

    print("Tentando Agente Local via AGY CLI (Autenticação IDE)...")
    try:
        ide_url = subprocess.check_output(["agy", "-p", prompt_ide], text=True).strip()
        agents_url = subprocess.check_output(["agy", "-p", prompt_agents], text=True).strip()
        
        if ide_url.startswith("http") and agents_url.startswith("http"):
            return ide_url, agents_url
    except Exception as e:
        print(f"AGY CLI falhou ou não encontrado: {e}")
    
    print("Tentando Agente em Nuvem via Google Antigravity SDK (Autenticação GEMINI_API_KEY)...")
    try:
        from google.antigravity import Agent, LocalAgentConfig
        if not os.environ.get("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY not found in environment.")

        async def _run_agent():
            config = LocalAgentConfig()
            async with Agent(config=config) as agent:
                ide_res = await agent.chat(prompt_ide)
                agents_res = await agent.chat(prompt_agents)
                return ide_res.text.strip(), agents_res.text.strip()
                
        ide_url, agents_url = asyncio.run(_run_agent())
        if ide_url.startswith("http") and agents_url.startswith("http"):
            return ide_url, agents_url
    except ImportError:
        print("SDK google-antigravity não instalado.")
    except Exception as e:
        print(f"Agente SDK falhou: {e}")
        
    print("Usando URLs de fallback (estáticas)...")
    return _fallback_urls()

def download_file(url, dest_path):
    print(f"Baixando {url} para {dest_path}...")
    urllib.request.urlretrieve(url, dest_path)
    print("Download concluído.")

def create_rpm_spec(ide_tar_name, agents_tar_name):
    spec_content = textwrap.dedent(f"""\
        Name:           antigravity-suite
        Version:        2.0.0
        Release:        1%{{?dist}}
        Summary:        Antigravity IDE and Agents Suite
        License:        MIT
        URL:            https://antigravity.google
        Source0:        %{{name}}-%{{version}}.tar.gz
        
        # Source1: {ide_tar_name}
        # Source2: {agents_tar_name}

        %description
        Pacote completo contendo o Antigravity IDE e o Antigravity Agents para Linux x64.
        
        %prep
        tar -xzf %{{_sourcedir}}/{ide_tar_name} -C .
        tar -xzf %{{_sourcedir}}/{agents_tar_name} -C .

        %install
        rm -rf %{{buildroot}}
        mkdir -p %{{buildroot}}/opt/antigravity-ide
        mkdir -p %{{buildroot}}/usr/share/antigravity

        cp -rp "Antigravity IDE"/* %{{buildroot}}/opt/antigravity-ide/
        cp -rp "Antigravity-x64"/* %{{buildroot}}/usr/share/antigravity/
        
        %post
        ln -sf /opt/antigravity-ide/antigravity-ide /usr/bin/antigravity-ide
        ln -sf /usr/share/antigravity/antigravity /usr/bin/antigravity

        DESKTOP_DIR="/usr/share/applications"
        cat <<EOF > $DESKTOP_DIR/antigravity-ide.desktop
        [Desktop Entry]
        Name=Antigravity IDE
        Exec=/opt/antigravity-ide/antigravity-ide %F
        Icon=/opt/antigravity-ide/resources/app/resources/linux/code.png
        Type=Application
        Categories=Development;IDE;
        EOF
        chmod 755 $DESKTOP_DIR/antigravity-ide.desktop

        cat <<EOF > $DESKTOP_DIR/antigravity.desktop
        [Desktop Entry]
        Name=Antigravity
        Exec=/usr/share/antigravity/antigravity %F
        Icon=/usr/share/pixmaps/antigravity.png
        Type=Application
        Categories=Development;IDE;
        EOF
        chmod 755 $DESKTOP_DIR/antigravity.desktop

        %files
        /opt/antigravity-ide/
        /usr/share/antigravity/
        
        %clean
        rm -rf %{{buildroot}}
    """)
    spec_path = RPMBUILD_DIR / "SPECS" / "antigravity-suite.spec"
    with open(spec_path, "w") as f:
        f.write(spec_content)
    return spec_path

def build_rpm(ide_filename, agents_filename):
    print("\\n=== Construindo RPM ===")
    for d in ["BUILD", "RPMS", "SOURCES", "SPECS", "SRPMS"]:
        (RPMBUILD_DIR / d).mkdir(parents=True, exist_ok=True)
    
    ide_dest = RPMBUILD_DIR / "SOURCES" / ide_filename
    agents_dest = RPMBUILD_DIR / "SOURCES" / agents_filename
    
    if not ide_dest.exists():
        download_file(ide_url, ide_dest)
    if not agents_dest.exists():
        download_file(agents_url, agents_dest)
        
    spec_path = create_rpm_spec(ide_filename, agents_filename)
    
    try:
        subprocess.run(["rpmbuild", "-bb", str(spec_path)], check=True)
        print("\\nRPM gerado com sucesso em: ~/rpmbuild/RPMS/x86_64/")
    except FileNotFoundError:
        print("ERRO: 'rpmbuild' não encontrado.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao gerar RPM: {e}")

def build_deb(ide_url, agents_url):
    print("\\n=== Construindo DEB ===")
    
    if DEBBUILD_DIR.exists():
        shutil.rmtree(DEBBUILD_DIR)
        
    os.makedirs(DEBBUILD_DIR / "DEBIAN", exist_ok=True)
    os.makedirs(DEBBUILD_DIR / "opt" / "antigravity-ide", exist_ok=True)
    os.makedirs(DEBBUILD_DIR / "usr" / "share" / "antigravity", exist_ok=True)
    os.makedirs(DEBBUILD_DIR / "usr" / "bin", exist_ok=True)
    os.makedirs(DEBBUILD_DIR / "usr" / "share" / "applications", exist_ok=True)

    # Control file
    control_content = textwrap.dedent("""\
        Package: antigravity-suite
        Version: 2.0.0-1
        Section: devel
        Priority: optional
        Architecture: amd64
        Maintainer: RLuf <contato@rluf.com>
        Description: Antigravity IDE and Agents Suite
    """)
    with open(DEBBUILD_DIR / "DEBIAN" / "control", "w") as f:
        f.write(control_content)

    # Postinst
    postinst_content = textwrap.dedent("""\
        #!/bin/bash
        ln -sf /opt/antigravity-ide/antigravity-ide /usr/bin/antigravity-ide
        ln -sf /usr/share/antigravity/antigravity /usr/bin/antigravity
    """)
    postinst_path = DEBBUILD_DIR / "DEBIAN" / "postinst"
    with open(postinst_path, "w") as f:
        f.write(postinst_content)
    os.chmod(postinst_path, 0o755)

    # Desktop files
    desktop_ide = textwrap.dedent("""\
        [Desktop Entry]
        Name=Antigravity IDE
        Exec=/opt/antigravity-ide/antigravity-ide %F
        Icon=/opt/antigravity-ide/resources/app/resources/linux/code.png
        Type=Application
        Categories=Development;IDE;
    """)
    with open(DEBBUILD_DIR / "usr" / "share" / "applications" / "antigravity-ide.desktop", "w") as f:
        f.write(desktop_ide)

    desktop_agents = textwrap.dedent("""\
        [Desktop Entry]
        Name=Antigravity
        Exec=/usr/share/antigravity/antigravity %F
        Icon=/usr/share/pixmaps/antigravity.png
        Type=Application
        Categories=Development;IDE;
    """)
    with open(DEBBUILD_DIR / "usr" / "share" / "applications" / "antigravity.desktop", "w") as f:
        f.write(desktop_agents)

    # Download and extract directly into debbuild root
    tmp_dir = Path.home() / "debbuild" / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    ide_tar = tmp_dir / "ide.tar.gz"
    agents_tar = tmp_dir / "agents.tar.gz"
    
    download_file(ide_url, ide_tar)
    download_file(agents_url, agents_tar)

    print("Extraindo IDE...")
    subprocess.run(["tar", "-xzf", str(ide_tar), "-C", str(tmp_dir)], check=True)
    subprocess.run(["cp", "-rp", str(tmp_dir / "Antigravity IDE" / "."), str(DEBBUILD_DIR / "opt" / "antigravity-ide")], check=True)
    
    print("Extraindo Agents...")
    subprocess.run(["tar", "-xzf", str(agents_tar), "-C", str(tmp_dir)], check=True)
    subprocess.run(["cp", "-rp", str(tmp_dir / "Antigravity-x64" / "."), str(DEBBUILD_DIR / "usr" / "share" / "antigravity")], check=True)
    
    try:
        subprocess.run(["dpkg-deb", "--build", str(DEBBUILD_DIR)], check=True)
        print("\\nDEB gerado com sucesso em: ~/debbuild/antigravity-suite_2.0.0-1_amd64.deb")
    except FileNotFoundError:
        print("ERRO: 'dpkg-deb' não encontrado.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao gerar DEB: {e}")
        
    shutil.rmtree(tmp_dir)

def main():
    print("=== Antigravity Autobuilder (RPM & DEB) ===")
    
    global ide_url, agents_url
    ide_url, agents_url = fetch_download_links()
    print(f"Link do IDE resolvido: {ide_url}")
    print(f"Link do Agents resolvido: {agents_url}")

    if shutil.which("rpmbuild"):
        build_rpm("Antigravity_IDE.tar.gz", "Antigravity.tar.gz")
    else:
        print("Pulando build RPM (rpmbuild não instalado).")
        
    if shutil.which("dpkg-deb"):
        build_deb(ide_url, agents_url)
    else:
        print("Pulando build DEB (dpkg-deb não instalado).")

if __name__ == "__main__":
    main()
