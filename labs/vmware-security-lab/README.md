# Laboratório de Cibersegurança e Redes — VMware

**Registro público de estudo e laboratório. Atualizado em 17/11/2026.**  
**Escopo:** infraestrutura pessoal e VMs próprias, sem exposição de configurações, credenciais ou dados de clientes.

## Objetivo

Estou montando um laboratório no VMware Workstation para praticar administração de redes, Windows Server, Active Directory, Linux, firewall, diagnóstico, monitoramento e, em fases posteriores, Red/Purple Team e análise de malware. O objetivo não é instalar muitas ferramentas; é conseguir configurar, validar, identificar falhas, corrigir e documentar.

Os estados abaixo diferenciam **validado**, **existente com configuração parcial** e **planejado**. VM criada não significa competência dominada ou serviço operacional.

## Arquitetura e zonas

```text
VMware Workstation
  |
  +-- FW01-PFSENSE (gateway)
  |     |
  |     +-- LAB-CORP [em uso]
  |     |     +-- DC01          Windows Server 2022 / AD DS / DNS
  |     |     +-- WIN11-VULN01 Windows 11 Pro / membro do domínio
  |     |     +-- LINUX01      serviços Linux (verificação pendente)
  |     |
  |     +-- LAB-RED [organização pretendida]
  |     |     +-- KALI01       testes autorizados
  |     |
  |     +-- LAB-SOC [organização pretendida]
  |           +-- WAZUH01     monitoramento / investigação
  |
  +-- MALWARE-LAB [LAN Segment separado; isolamento completo pendente]
        +-- MALWARE01          Windows 11 de análise
        +-- REMNUX01           Linux de apoio
```

**Atenção:** o desenho representa funções e limites pretendidos, não comprova que toda segmentação de LAB-RED/LAB-SOC e toda integração entre as VMs esteja concluída. O segmento de malware não deve ser roteado para as demais redes.

## Inventário de VMs

| VM | Papel | Estado observado |
| --- | --- | --- |
| FW01-PFSENSE | Gateway, DHCP, resolução/encaminhamento DNS, regras | Em uso na rede corporativa do laboratório; cobertura completa de regras e VPN ainda não documentada |
| DC01 | Windows Server 2022 Standard Evaluation; AD DS e DNS | Floresta e domínio `corp.test` criados; testes DNS e serviços validados |
| WIN11-VULN01 | Windows 11 Pro; endpoint membro | Ingresso em `corp.test`, logon de domínio e resolução de serviços AD validados; não implica que esteja vulnerável por configuração |
| LINUX01 | Servidor Linux para permissões, logs e serviços | Existe no inventário; papel e configuração atual a reconferir |
| KALI01 | Estação para testes de segurança autorizados | VM existente; baseline/rede e ferramentas precisam de validação atual |
| WAZUH01 | Monitoramento e investigação | VM registrada; coleta de agentes e cobertura não certificadas |
| MALWARE01 | Windows 11 descartável para análise | Comunicação local com REMNUX01 testada; contenção completa ainda pendente |
| REMNUX01 | Linux para captura e análise | Comunicação local testada; IP configurado por comando temporário no teste |

**Planejado, mas não contado como VM existente:** SRV01 (Windows Server membro / SMB + NTFS), sensores e ferramentas adicionais somente quando os estudos exigirem.

## LAB-CORP: o que foi feito

- VMware: DC01 e WIN11-VULN01 na rede de laboratório associada ao pfSense.
- Endereçamento observado: pfSense `192.168.20.1`, DC01 `192.168.20.10/24` (fixo). WIN11 recebeu `192.168.20.108` por DHCP em um teste de outubro; leases podem mudar.
- Faixa DHCP reportada no pfSense: `192.168.20.100–192.168.20.200`.
- DC01: hostname definitivo, papel AD DS e DNS, floresta `corp.test` com NetBIOS `CORP`.
- DNS do DC: registros de descoberta AD; consultas externas encaminhadas ao pfSense (`192.168.20.1`).
- WIN11-VULN01: DNS apontado para o DC; `nslookup` e registro SRV LDAP testados; ingresso no domínio, autenticação e `systeminfo` confirmados.
- No ADUC (`dsa.msc`), criadas as OUs `Usuarios`, `Computadores`, `Servidores` e `Grupos`. O objeto da estação foi movido de `Computers` para `OU=Computadores`; o container padrão foi preservado.
- Estudo introdutório de forest, domain, DC, OU/container, DN, CN, UPN, sAMAccountName, SID e diferença entre OU e grupo.

### Evidências dos testes

| Verificação | Resultado observado | Limitação |
| --- | --- | --- |
| `Get-ADDomain` e `Get-ADForest` | `corp.test` identificado, DC01 com papéis FSMO de domínio/floresta | Um único DC; sem redundância |
| `Get-Service NTDS,DNS` | Serviços `Running` | Não prova alta disponibilidade |
| `dcdiag /test:dns` | `DC01 passed test DNS` e `corp.test passed test DNS` | Verificação pontual |
| `nslookup dc01.corp.test` | Endereço do DC resolvido | Teste feito na estação após corrigir DNS |
| `nslookup -type=SRV _ldap._tcp.dc._msdcs.corp.test` | Localização do `dc01.corp.test`, LDAP 389 | Não equivale a auditoria completa do AD |
| `whoami` e `systeminfo` na WIN11 | `corp\administrator`, domínio `corp.test`, servidor de logon `\\DC01` | Uso de conta administrativa foi apenas para validar ingresso |

### Diagnósticos executados

1. **IP APIPA no DC01:** inicialmente `169.254.x.x`. Verificado DHCP e conectividade; DC recebeu lease na LAB-CORP antes do IP fixo.
2. **DNS externo com falha:** consulta local devolvia `SERVFAIL`; consulta direta ao pfSense respondia. Ajustado forwarder DNS do DC; nomes externos e SRV do AD foram testados novamente.
3. **Cliente consultando DNS incorreto:** WIN11 usava pfSense e não resolvia `corp.test`. Alterado o DNS da estação para o DC e confirmada descoberta do controlador.
4. **Ping só em um sentido:** o ICMP de entrada da estação não respondeu, mas houve ARP e testes necessários para ingresso no domínio. A falha de ping isoladamente não foi tratada como falha de Active Directory.

## MALWARE-LAB: estado e limites

- VMs `MALWARE01` e `REMNUX01` com adaptador em LAN Segment `MALWARE-LAB` nos testes.
- IPv4 de teste: `10.66.66.10/24` e `10.66.66.20/24`.
- Comunicação ICMP interna nos dois sentidos confirmada após ajuste da regra ICMP no Windows.
- Ausência de rota padrão IPv4 observada nas duas VMs; tentativas de IP externo falharam.
- **O IP do REMNUX foi configurado temporariamente** e pode desaparecer após reinício.

**Ainda não validado:** ausência de caminhos por IPv6, adaptadores adicionais, clipboard, drag-and-drop, pastas compartilhadas, dispositivos conectados, túneis/proxies e outros canais entre host e guest. Falta baseline limpa, recuperação e validação pós-migração. Não executar amostras reais antes dessa etapa.

## Outras VMs e backlog

- **LINUX01:** serviços Linux, usuários, permissões, redes e logs.
- **KALI01:** reconhecimento e testes de segurança exclusivamente em VMs próprias ou plataformas autorizadas.
- **WAZUH01:** receber telemetria, correlacionar eventos e apoiar investigações; cobertura e agentes ainda precisam de testes.
- **SRV01 (futuro):** servidor de arquivos membro do domínio; grupos, SMB, NTFS, herança, permissões efetivas e caso prático de acesso negado.
- **Samba (futuro):** comparação entre Windows Server + NTFS ACL e Linux + Samba/ACL após dominar o cenário Windows.

Estes itens não viram cursos ou focos paralelos automaticamente.

## Evidência e publicação

- Prints precisam ser de **VMs próprias**, preferencialmente com hostname, IPs privados de teste e resultados técnicos legíveis.
- Nunca publicar usuários/arquivos de clientes, segredos, tokens, senhas, sessões, credenciais ou configurações reais do trabalho.
- Um print de comando mostra uma observação pontual, não prova sozinho causalidade, isolamento total ou domínio da ferramenta.
- Registrar cenário, hipótese, teste, resultado, alteração e reteste quando aplicável.
- Snapshots ajudam a restaurar estados; **snapshot não é backup**.

A página principal do portfólio, com a visualização resumida e registros transcritos, é [Laboratório técnico](../../laboratorio.html).
