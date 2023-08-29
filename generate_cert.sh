#!/bin/bash
printf "
*******************************
** ::CERTIFICATE GENERATOR:: **
*******************************
"
if [ -e /etc/ssl/openssl.cnf ]
then
  CNF="/etc/ssl/openssl.cnf" #Ubuntu
elif [ -e /etc/pki/tls/openssl.cnf ]
then
  CNF="/etc/pki/tls/openssl.cnf" #Fedora, rhel and alike ...
else
  echo "Can't locate openssl.cnf, locate it and update this script"
  exit 1
fi

if [ -n "$1" ]
then
 
    # Store certificate dns names
    export CERTDNS=("$@")
    # Format for openssl.cnf temporary req additions
    export SUBJALTNAMES=$(printf "subjectAltName="; declare -i i=1; declare -x x=1; for j in ${CERTDNS[@]}; do if [[ $j =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then printf IP.$x:$j,;x=$x+1; else printf DNS.$i:$j,;i=$i+1;fi;done | sed "s/,$//")
    # Create RSA key or reuse old one (notice, key naming needs to match for key to be reused)
    if [[ -e ${CERTDNS[0]}.key ]]; then
      echo "<1> Using existing key file '${CERTDNS[0]}.key'"
    else
      echo "<1> Generating key '${CERTDNS[0]}.key'"
      umask 077 ; openssl genrsa 4096 > ${CERTDNS[0]}.key 2>/dev/null; umask 022
    fi
    # Generate that CSR
    echo "<2> Generating CSR '${CERTDNS[0]}.req'"
    openssl req -utf8 -new -sha256 -key ${CERTDNS[0]}.key -subj "/CN=${CERTDNS[0]}/ST=Västra Götalands län/O=AB Company/C=SE" -reqexts SAN -config <(cat $CNF <(printf "[SAN]\n$SUBJALTNAMES")) -out ${CERTDNS[0]}.req
    # Verify that your .req file contains desired attributes:
    echo "<3> DONE, execute below to revies/verify your request:"
    printf "
    openssl req -in ${CERTDNS[0]}.req -noout -text
    "
else
    printf "
     Missing fqdn, ex)
                $0 name.company.com
                $0 name.company.com othername.company.com shortname
                $0 name.company.com othername.company.com 1.1.2.3
   
"
fi
printf "
/j0nix @ Conoa 😎 
"
