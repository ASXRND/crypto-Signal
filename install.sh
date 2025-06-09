#!/bin/bash

echo "Starting Crypto Signal installation..."

# Установка системных зависимостей
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y build-essential wget python3-pip python3-dev

# Установка TA-LIB
echo "Installing TA-LIB..."
cd ~
wget https://github.com/ta-lib/ta-lib/releases/download/v0.6.4/ta-lib-0.6.4-src.tar.gz
tar -xvzf ta-lib-0.6.4-src.tar.gz
cd ta-lib-0.6.4
./configure --prefix=/usr
make -j$(nproc)
sudo make install

# Установка переменных окружения для TA-LIB
echo "Setting up TA-LIB environment variables..."
export TA_INCLUDE_PATH=/usr/include
export TA_LIBRARY_PATH=/usr/lib

# Добавление переменных в .bashrc для постоянного эффекта
echo "export TA_INCLUDE_PATH=/usr/include" >> ~/.bashrc
echo "export TA_LIBRARY_PATH=/usr/lib" >> ~/.bashrc

# Создание директории для логов
echo "Creating logs directory..."
mkdir -p logs

# Установка Python зависимостей
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Installation completed!"
echo "You can now run the application with: python3 app/app.py"
