/***************************************************************************/
// File			  [node.h]
// Author		  [Erik Kuo, Joshua Lin]
// Synopsis		[Code for managing car movement when encounter a node]
// Functions  [/* add on your own! */]
// Modify		  [2020/03/027 Erik Kuo]
/***************************************************************************/

/*===========================import variable===========================*/
int extern Tp; //use Tp directly, don't need to implement it, it is defined in midterm_project.ino 
//int extern M;
/*===========================import variable===========================*/

// TODO: add some function to control your car when encounter a node
// here are something you can try: left_turn, right_turn... etc.
void Stop() {
    MotorWriting(0, 0);
}

void TurnRight(int pin) {
    // pin : the middle IR --*--
    int m;
    do {
        MotorWriting(200, 200);
        m = (analogRead(pin) > 100);
    } while(m == 1); 

    do {
        MotorWriting(150, -150);
        m = (analogRead(M) > 100);
    } while(m == 0); 
  
    Stop();
}

void TurnLeft(int pin) {
    // pin : the middle IR --*--
    int m;
    do {
        MotorWriting(200, 200);
        m = (analogRead(pin) > 100);
    } while(m == 1); 

    do {
        MotorWriting(-150, 150);
        m = (analogRead(pin) > 100);
    } while(m == 0); 
  
    Stop();
}

void TurnBack(int pin) {
    // pin : the middle IR --*--
    MotorWriting(-150, 150);
    delay(600); 
    int m = (analogRead(pin) > 100);
    while(m == 0) {
        MotorWriting(-150, 150);
        m = (analogRead(pin) > 100);
    }
    Stop();
}

void Moveforward(int pin1, int pin2, int pin3, int pin4, int pin5) {
    int l3 = (analogRead(L3) > 100) ? 1 : 0;
    int l2 = (analogRead(L2) > 100) ? 1 : 0;
    int m  = (analogRead(M)  > 100) ? 1 : 0;
    int r2 = (analogRead(R2) > 100) ? 1 : 0;
    int r3 = (analogRead(R3) > 100) ? 1 : 0;

    while (!(l3 == 1 && l2 == 1 && m == 1 && r2 == 1 && r3 == 1)) {    
        Tracking_P(vL, vR);
        l3 = (analogRead(L3) > 100) ? 1 : 0;
        l2 = (analogRead(L2) > 100) ? 1 : 0;
        m  = (analogRead(M)  > 100) ? 1 : 0;
        r2 = (analogRead(R2) > 100) ? 1 : 0;
        r3 = (analogRead(R3) > 100) ? 1 : 0;
    }
  
    Stop(); 
    delay(100); 
}