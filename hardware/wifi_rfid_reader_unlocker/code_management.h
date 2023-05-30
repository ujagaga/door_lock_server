#ifndef CODE_MANAGEMENT_H
#define CODE_MANAGEMENT_H

extern void CM_reportCode(String code);
extern void CM_init(void);
extern void CM_saveLatestCode(void);
extern void CM_clearCodes(void);
extern String CM_getUnsavedCode(void);
extern int CM_getNumberOfSavedCodes(void);
extern bool CM_checkCodeSaved(void);

#endif
