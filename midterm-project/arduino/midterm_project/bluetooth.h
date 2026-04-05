/***************************************************************************/
// File       [bluetooth.h]
// Author     [Lumos, Hsinchi]
// Synopsis   [Code for bluetooth communication]
// Functions  [ask_BT, send_msg, send_byte]
// Modify     [2026/04/05 Lumos]
/***************************************************************************/

enum BT_CMD {
    NOTHING,
    START,
    HALT,
    LEFT_TURN,
    MOVE_FORWARD,
    RIGHT_TURN,
    BACKWARD
};

/*
 * Polls the Serial3 interface for incoming Bluetooth bytes
 * and maps them to the corresponding BT_CMD enum.
 */
BT_CMD ask_BT() {
    BT_CMD message = NOTHING;
    char cmd;
    if (Serial3.available()) {
        cmd = Serial3.read();
        switch(cmd) {
            case 's': message = START; break;
            case 'h': message = HALT; break;
            case 'l': message = LEFT_TURN; break;
            case 'f': message = MOVE_FORWARD; break;
            case 'r': message = RIGHT_TURN; break;
            case 'b': message = BACKWARD; break;
            default:  message = NOTHING;
        }

#ifdef DEBUG
        Serial.print("cmd : ");
        Serial.println(cmd);
#endif
    }
    return message;
}

/*
 * Transmits a single character message over Bluetooth.
 */
void send_msg(const char& msg) {
    Serial3.print(msg);

#ifdef DEBUG
    Serial.print("Sent msg to BT: ");
    Serial.println(msg);
#endif
}

/*
 * Transmits an array of bytes (e.g., RFID UID) over Bluetooth.
 */
void send_byte(byte* id, byte& idSize) {
    for (byte i = 0; i < idSize; i++) {
        Serial3.print(id[i]);
    }

#ifdef DEBUG
    Serial.print("Sent id: ");
    for (byte i = 0; i < idSize; i++) {
        Serial.print(id[i], HEX);
    }
    Serial.println();
#endif
}