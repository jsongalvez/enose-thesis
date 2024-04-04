#include <stdio.h>
#include <wiringPi.h>

// Set pins
//   Uses wiringpi pins (wPi)

#define DT_PIN 19
#define CLK_PIN 20
#define SW_PIN 16

static volatile int DT = 1;
static volatile int CLK = 1;
static volatile int SW = 0;

void rotaryChange (void) {
	DT = digitalRead(DT_PIN);
	CLK = digitalRead(CLK_PIN);
	printf ("%i %i\n",DT, CLK);	
}

int main () {
	wiringPiSetup ();
	
	pullUpDnControl (DT_PIN, PUD_OFF);
	pullUpDnControl (CLK_PIN, PUD_OFF);
	
	pinMode(DT_PIN, INPUT);
	pinMode(CLK_PIN, INPUT);

	wiringPiISR (DT_PIN, INT_EDGE_BOTH, &rotaryChange);
	wiringPiISR (CLK_PIN, INT_EDGE_BOTH, &rotaryChange);
	
	while (1) {}

	return 0;
}

