#!/bin/bash

echo " Iniciando Actualizacion "
sleep 2
echo "Actualizaremos tu sistema en unos momentos ......"
sleep 3
echo "Esto podria tardar ya que vamos a limpiar el sistema de dependencias inutiles, cache y basura del sistema."
sleep 2

set -e

sudo apt update
sudo apt upgrade -y
sudo apt full-upgrade -y

echo "Limpiando dependencias..."
sudo apt autoremove -y
sudo apt autoremove --purge -y

echo "Limpiando cache de APT..."
sudo apt clean
sudo apt autoclean

echo "Limpiando Flatpaks que no uses..."
flatpak uninstall --unused -y 2>/dev/null || true

echo "Eliminando configuraciones huérfanas..."
orphans=$(dpkg -l | awk '/^rc/ {print $2}')

if [ -n "$orphans" ]; then
    echo "$orphans" | xargs sudo dpkg --purge
else
    echo "No hay configuraciones huérfanas."
fi

echo "Limpiando cache del usuario..."
rm -rf ~/.cache/*

echo "Listo. Sistema actualizado y limpio."
sleep 1
echo "Operación completada."
sleep 3
clear
