#ifndef PINCTRL_H
#define PINCTRL_H

extern void PINCTRL_trigger(void);
extern void PINCTRL_init(void);
extern void PINCTRL_process(void);
extern bool PINCTRL_reset_requested(void);

#endif
