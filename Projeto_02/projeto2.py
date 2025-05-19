#//////////////////////////////////////////////////////////////////
#//   EA801A - Laboratório de projetos de sistemas embarcados.   //
#//   Equipe: Dupla 03.                                          //
#//   Integrantes:                                               //
#//   Antonio Francisco Morino Neto, RA: 194308;                 //
#//   Otávio Briske Lima, RA: 220716;                            //
#//   Pedro Gimeno de Oliveira, RA: 239934 .                     //
#//   Projeto 02 - Pokédex.                                      //
#//   Campinas, 2025.                                            //
#//////////////////////////////////////////////////////////////////

#//////////////////////////////
#// Importação de Recursos: //
#//////////////////////////////

from dfplayermini import DFPlayerMini  # Importa os recursos utilizados pelo DFPlayer da biblioteca "dfplayermini.py"
from machine import Pin                # Importa as funcionalidades de controle de pinos da Raspberry Pi Pico W
import time                            # Importa o módulo time, utilizado para temporização
import neopixel                        # Importa o módulo neopixel para controle da matriz RGB

#///////////////////////////////////////////////////////
#//  Inicialização do DFPlayer: configura a UART0,    //
#//  define volume, escolhe a fonte e inicia a faixa  //
#///////////////////////////////////////////////////////

player = DFPlayerMini(0, 16, 17)  # Instancia o player com UART0, TX no GPIO 16 e RX no GPIO 17
player.reset()                    # Reinicia o DFPlayer para garantir que inicie corretamente
time.sleep(1)                     # Aguarda 1 segundo após o reset
player.set_volume(12)            # Define o volume inicial em 12 (escala de 0 a 30) para que a mudança de volume seja mais evidente
player.select_source('sdcard')   # Seleciona o cartão SD como fonte de música
player.play(1)                   # Começa a tocar a faixa 1

#//////////////////////////////
#//   Variáveis de Estado:  //
#//////////////////////////////

music_playing = True             # Indica se a música está atualmente tocando
current_track = 1               # Número da faixa atual
volume = 12                    # Volume inicial
max_tracks = 20                # Número máximo de faixas disponíveis no SD

#//////////////////////////////////
#//    Configuração dos botões: //
#//////////////////////////////////

pause_button = Pin(5, Pin.IN, Pin.PULL_UP)   # Botão de pausa no GPIO 5, com pull-up interno
next_button = Pin(6, Pin.IN, Pin.PULL_UP)    # Botão de próxima música no GPIO 6, com pull-up interno

#//////////////////////////////////////////////////////
#// Tempo de referência (em ms) para diferenciar     //
#// entre toque curto e pressão longa nos botões     //
#//////////////////////////////////////////////////////

long_press_threshold = 400  # Se o botão for mantido pressionado por mais de 400ms, é considerado um toque longo

#/////////////////////////////////////////////////////////////////////
#//  Função que detecta se o botão foi pressionado brevemente       //
#//  ("short") ou por mais tempo ("long").                          //
#/////////////////////////////////////////////////////////////////////

def check_button_action(pin):
    if not pin.value():  # Se o botão foi pressionado (nível lógico LOW)
        press_time = time.ticks_ms()  # Marca o tempo de início da pressão
        while not pin.value():  # Enquanto o botão estiver pressionado
            if time.ticks_diff(time.ticks_ms(), press_time) > long_press_threshold:
                while not pin.value():  # Aguarda o botão ser solto
                    time.sleep_ms(10)
                return 'long'  # Pressionado por mais de 400ms → "long"
            time.sleep_ms(10)  # Espera antes de checar novamente
        return 'short'  # Pressionado por menos de 400ms → "short"
    return None  # Nenhuma ação detectada

#//////////////////////////////////////////////////////////////
#//         Loop principal que roda continuamente            //
#//  Atualiza a matriz de LEDs e responde aos botões         //
#//////////////////////////////////////////////////////////////

while True:

    #////////////////////////////////////////////
    #// Inicialização da Matriz de LEDs RGB:  //
    #////////////////////////////////////////////

    pin = machine.Pin(7)        # Define o pino GPIO 7 como saída para os LEDs
    np = neopixel.NeoPixel(pin, 25)  # Instancia uma matriz de 25 LEDs (5x5)

    #//////////////////////////////////////////////
    #// Definição das cores utilizadas na Pokébola //
    #//////////////////////////////////////////////

    RED = (40, 0, 0)           # Define cor vermelha com intensidade suave
    WHITE = (35, 35, 35)       # Define cor branca com intensidade moderada
    OFF = (0, 0, 0)            # Define LED apagado (sem cor)

    #///////////////////////////////////////////////////////////////
    #//   Mapeamento da Pokébola em formato de matriz 5x5 (linhas) //
    #//   A imagem foi invertida para alinhar com a ordem dos LEDs //
    #///////////////////////////////////////////////////////////////

    pokeball = [
        [OFF, WHITE, WHITE, WHITE, OFF],       # Linha 1
        [WHITE, WHITE, WHITE, WHITE, WHITE],   # Linha 2
        [RED, RED, WHITE, RED, RED],           # Linha 3
        [RED, RED, RED, RED, RED],             # Linha 4
        [OFF, RED, RED, RED, OFF]              # Linha 5
    ]

    #///////////////////////////////////////////////////
    #//   Animação da Pokébola piscando por linhas    //
    #//   Cada linha é atualizada com um pequeno delay //
    #///////////////////////////////////////////////////

    for row_index, row in enumerate(pokeball):
        for col_index, color in enumerate(row):
            led_index = row_index * 5 + col_index  # Calcula o índice do LED correspondente
            np[led_index] = color                  # Define a cor no LED
        np.write()  # Atualiza os LEDs da linha atual
        time.sleep(0.1)  # Pequeno delay entre as linhas para criar o efeito de piscar

    #///////////////////////////////////////////////////
    #//         Detecção de interação com botões      //
    #///////////////////////////////////////////////////

    action = check_button_action(pause_button)
    if action == 'short':
        # Pressionamento curto → alterna entre pausar e continuar a música
        if music_playing:
            player.pause()
            print("Música pausada")
        else:
            player.start()
            print("Música retomada")
        music_playing = not music_playing  # Atualiza o estado

    elif action == 'long':
        # Pressionamento longo → diminui o volume
        if volume > 0:
            volume -= 1
            player.set_volume(volume)
            print("Volume diminuído para", volume)

    action = check_button_action(next_button)
    if action == 'short':
        # Pressionamento curto → toca próxima faixa (com retorno à primeira após a última)
        current_track += 1
        if current_track > max_tracks:
            current_track = 1
        player.play(current_track)
        print("Tocando faixa", current_track)
        music_playing = True

    elif action == 'long':
        # Pressionamento longo → aumenta o volume
        if volume < 30:
            volume += 1
            player.set_volume(volume)
            print("Volume aumentado para", volume)

    time.sleep_ms(50)  # Pequeno atraso para evitar uso excessivo da CPU
