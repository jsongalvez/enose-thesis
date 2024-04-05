#include "st7735s_compat.h"
#include "wiringPiSPI.h"
#include "wiringPi.h"
#include "stdio.h"

#define CS_PIN    15
#define RES_PIN   6
#define DC_PIN    9
#define MOSI_PIN  11
#define SCK_PIN   14
#define BLK_PIN    0

#define SPI_CHANNEL 0
#define SPI_SPEED 500000 // 500 KHz
#define SPI_BUFFER_LEN 1 // 1 byte

void SPI_Init(void) {
    wiringPiSetup();
    wiringPiSPISetup(SPI_CHANNEL, SPI_SPEED);

    pinMode(CS_PIN, OUTPUT);
    pinMode(RES_PIN, OUTPUT);
    pinMode(DC_PIN, OUTPUT);
    pinMode(BLK_PIN, OUTPUT);
    pinMode(MOSI_PIN, OUTPUT);
    pinMode(SCK_PIN, OUTPUT);

    digitalWrite(CS_PIN, LOW);
    digitalWrite(RES_PIN, HIGH);
}

void Pin_CS_Low(void) {
    digitalWrite(CS_PIN, LOW);
}

void Pin_CS_High(void) {
    digitalWrite(CS_PIN, HIGH);
}

void Pin_RES_High(void) {
    digitalWrite(RES_PIN, HIGH);
}

void Pin_RES_Low(void) {
    digitalWrite(RES_PIN, LOW);
}

void Pin_DC_High(void) {
    digitalWrite(DC_PIN, HIGH);
}

void Pin_DC_Low(void) {
    digitalWrite(DC_PIN, LOW);
}
extern uint8_t backlight_pct;
void Pin_BLK_Pct(uint8_t pct) {
	backlight_pct = pct;
    // or connect to PWM output
    digitalWrite(BLK_PIN, HIGH);
}

void SPI_send(uint16_t len, uint8_t *data) {
    Pin_CS_Low();
    wiringPiSPIDataRW(SPI_CHANNEL, data, len);
    Pin_CS_High();
}

void SPI_TransmitCmd(uint16_t len, uint8_t *data) {
    Pin_DC_Low();
    SPI_send(len, data);
}

void SPI_TransmitData(uint16_t len, uint8_t *data) {
    Pin_DC_High();
    SPI_send(len, data);
}

void SPI_Transmit(uint16_t len, uint8_t *data) {
     SPI_TransmitCmd(1, data++);
     if (--len)
        SPI_TransmitData(len, data);
}

void _Delay(uint32_t d) {
    uint32_t m = millis();
    while (millis() - m < d) ;
}

