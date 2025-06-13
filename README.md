# 🚗 Driver Anti-Sleeping Alarm System

## 📖 Overview
This is a **real-time driver drowsiness detection system** using a laptop camera (OpenCV + MediaPipe).  
When sleepiness is detected (eye closure or yawning), a signal is sent via **UART** to the **STM32F103C8T6** microcontroller to trigger a blinking LED alert.

The system integrates a Python-based vision module with STM32 using the **CP2102 USB-UART** module.

---

## 🧰 Hardware Requirements
- STM32F103C8T6 “Blue Pill”
- ST-Link V2
- USB-UART (CP2102)
- LED
- Resistors
- Jumper wires (Male-to-Female or Male-to-Male)

---

## 💻 Software Requirements
- [STM32CubeIDE](https://www.st.com/en/development-tools/stm32cubeide.html)
- [Visual Studio Code](https://code.visualstudio.com/)
- Python Libraries:
  ```bash
  pip install opencv-python mediapipe pyserial

## 🔌 Hardware Connections

### 1. Connect ST-Link V2 to STM32F103C8T6

| ST-Link V2 | STM32F103C8T6 |
|------------|---------------|
| VCC (3.3V) | 3.3V          |
| GND        | GND           |
| SWDIO      | PA13          |
| SWCLK      | PA14          |

### 2. Connect USB-UART (PL2303HX) to STM32F103C8T6

| PL2303HX    | STM32F103C8T6    |
|-------------|------------------|
| VCC (3.3V)  | 3.3V             |
| GND         | GND              |
| TXD         | PA10 (USART1 RX) |
| RXD         | PA9  (USART1 TX) |

> ⚠️ **Note:** Make sure to cross-connect TX → RX and RX → TX.

## 🧠 Functionality

- 🖥️ **Python (Laptop)**:
  - Uses **OpenCV** and **MediaPipe** to detect:
    - Eye closure (drowsiness)
    - Yawning (fatigue)
- 🔄 **Serial Communication**:
  - Sends character `'1'` from PC to STM32 via **UART** when drowsiness detected.
- 💡 **STM32 Microcontroller**:
  - On receiving `'1'`, it blinks an LED on **GPIOC Pin 13** as a visual alert.
## 🧾 STM32 Code (Sample)

```c
UART_HandleTypeDef huart1;

void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_USART1_UART_Init(void);

int main(void)
{
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();
  MX_USART1_UART_Init();

  uint8_t rx_data;

  while (1)
  {
    if (HAL_UART_Receive(&huart1, &rx_data, 1, HAL_MAX_DELAY) == HAL_OK)
    {
      if (rx_data == '1')
      {
        for (int i = 0; i < 5; i++) // Blink 5 times
        {
          HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET); // Turn on LED
          HAL_Delay(200);
          HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);   // Turn off LED
          HAL_Delay(200);
        }
      }
    }
  }
}
