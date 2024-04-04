#include <stdio.h>
#include <wiringPi.h>

#define DT_PIN 19
#define CLK_PIN 20
#define SW_PIN 16

unsigned long last_debounce = 0;
unsigned long debounce_delay = 2;

int main () {
    wiringPiSetup ();

    pinMode (DT_PIN, INPUT);
    pinMode (CLK_PIN, INPUT);
    pinMode (SW_PIN, INPUT);
    
    pullUpDnControl (DT_PIN, PUD_DOWN);
    pullUpDnControl (CLK_PIN, PUD_DOWN);
    pullUpDnControl (SW_PIN, PUD_DOWN);

    int dt_val, clk_val, sw_val = 0;
    int last_status, new_status = 0b000;
    int transition = 0b0000;
    int ctr = 0;
    int rot = 0;
	for (;;) {
        if (millis() - last_debounce > debounce_delay) {
            last_debounce = millis();

            last_status = (dt_val << 2) | (clk_val << 1) | sw_val;
            dt_val = digitalRead (DT_PIN);
            clk_val = digitalRead (CLK_PIN);
            sw_val = digitalRead (SW_PIN);

            new_status = (dt_val << 2) | (clk_val << 1) | sw_val;

            if (last_status == new_status) {
               continue;
            }
            transition = ((last_status >> 1) << 2) | (new_status >> 1);
            if (transition == 0b1110) {
                rot++;
            }
            else if (transition == 0b1101) {
                rot--;
            }
            printf("%i:\t%i %i %i\t%i %b\n", ctr++, dt_val, clk_val, sw_val, rot, transition);
        }
	}
	return 0;
}
