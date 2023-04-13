#ifndef HTTP_CLIENT_H
#define HTTP_CLIENT_H

extern void HTTPC_init(void);
extern void HTTPC_process(void);
extern void HTTPC_confirmLifesign(void);
extern void HTTPC_reportCode(String code);

#endif
