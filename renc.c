#include <stdio.h>
#include <wiringPi.h>

// Set pins
//   Uses wiringpi pins (wPi)

#define DT_PIN 19
#define CLK_PIN 20
#define SW_PIN 16

int DT = 0;
int CLK = 0;
int SW = 0;

void rotaryChange () {
	DT = digitalRead (DT_PIN);
	CLK = digitalRead (CLK_PIN);
	printf ("%i %i\n",DT, CLK);	
}

int main () {
	wiringPiSetup ();
	
	pullUpDnControl (DT_PIN, PUD_DOWN);
	pullUpDnControl (CLK_PIN, PUD_DOWN);

	wiringPiISR (DT_PIN, INT_EDGE_BOTH, &rotaryChange);
	wiringPiISR (CLK_PIN, INT_EDGE_BOTH, &rotaryChange);
	
	while (1) {}

	return 0;
}

