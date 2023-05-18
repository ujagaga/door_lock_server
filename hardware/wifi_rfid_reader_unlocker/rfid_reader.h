#ifndef RFID_H
#define RFID_H

extern void RFID_init(void);
extern void RFID_process(void);
extern void RFID_saveLastCode(void);
extern void RFID_clearCodes(void);
extern String RFID_getUnsavedCode(void);
extern bool RFID_isEepromClear(void);

#endif
