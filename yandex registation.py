# -*- coding: utf-8 -*-

import requests
import time

data = {
'continue': 'http://mail.google.com/mail/?pc=carousel-about-en',
'service': 'mail',
'f.req': '["AEThLlwxq4QDL5_E5yG6UPr6NK9me2JTzJdA_XnDQP2oAaF2ng6CThxJHf494-bkj6Wh9IV53Tolg_QXxeJqUVbBK_lkbuUYjJkCgUX9VsLcgBXrXFytWY3zttELwoNbT8WaResCKADOjpKuAx9_RPSHgFNK-8hjDIgdqAHx-MEQBIUmAsuREuE","avtobot","avtobot","avtobot","avtobot","ReBlack.RQ.1","684551qQ","ReBlack.RQ.2",true]',
'bgRequest': '["web-glif-signup","!q6ilqIlCIyXcKfW5ipFE0VShyjwW32cCAAAD-lIAAATcmQX7M6V226NmOFQiqetqMDzxFNt2ot0T99jDWi4FXwGb9wAuBEd2iRsKNPUnuuxkrKsyCRaDAKrfhDbpmJRj_ypYkEYJuar287MAs5i5P4jxgphMdJKgMHHjphSQuuVdEh7oU66KyLmirsSSq7sKmA3kgoEEwkbT-01fmUsbxFkWyYei5m0RPKXCWzCcB8jrtj7SqrUqSIOI3e-3twS4pjP7LQseUtRVPcU7AQgtfSp2TU3X0h0IEBqq1TUPp8YS5tGJFK0au6E2Gjjy3laGtV6g7UwwOEC26boCSmPi2kN7WJ5pIqFHgxtKJRUe_kquLlopzG28NYs48IVUy8oUdEAH1zew9y0kO-91xg9rnPCDhtg5P5zbgeQqlydYXl40oQgSE620zkCqe8Ouj3I9RefjfLMYo2jsKnOpfwGH3A7OB8NAy4tIAFeUOT09e6HGskb-q7Cjra7vUFDOStfp75G9yynzGE6ggya-FHLffgtHFtS094ZGKdaeSbvx1jWRoONOMPViO9mgJda8je93-3fnRcOOMtwdlaRMrSvchs57xawkL1JNug8k-mXivlC_9Y1CmyNpA9y05DWxycfzgCd0DD9Qy9haA1VvKInZPTG9pLRA-oVpDZjV2FSsZRICty_ihioenzwcZryhIy3y6GinN7afTO-ozsERQ50ezy6UCggf1ehxm_i9Dq8tFJ9e8vPNDnMQ073UVqKnWq6xgVrdmRw-bL2-ObyxpyIARcVHdC50PO86kdJee-KeEj245rJWLUHFOBQht78D_k7MCGoemLhsjUtRjQQG4bX0Z88K3AOw918T9RR0b0TmahEtp7gOLaiSwDnbDsactklpioVdp5Bc9L6NMoMKKL2jhNjv8cPb2o9Hn90odyA-L-me5yXekd68ohHfGSclzH-5' +
'8nZG8qYrky3459v-TBE6g1JrYPFUf]GOkJsq9x_rMpCHfaIi0vbZ6Gs60a2RUJWv6uCmfVvx1DwQxiXKTYA8wwcdUVCT1MbtTr1RDCSJQIbAzfQgx8-imX2IrjaVW5rxcpogR7bGyUE2jkXNJe236e1u9JFYVjgFJLt8ylnjQ6sfzvqtGvgk9wQMc_M_nItRMNTCVLsMcIy9atdcNIM443-QWhH9WbJCUT9OWujWJBCsvxaXhwSY7LNZ1uO7V3sfFWLOlyr6Hp7Vbr0_nY8pOQ0CPkjRn6YlSVvm3qJfqiCm5YIthNMrSWLBEvwVMCAGRtAUy0IR6roe2UQOMrBvL4cN9tZnbzITzppB5BgMNBDhWkQO6HOZANjjRUK8KGWn4dRLCw6-acVDSI__y5lFnB-t5_g-drC_NsXae_CoThGhp0Bww6ZWMil0MxPjf2ljXuGC9g3LIuS2a8oXKQcasWPSaGHtiXfT88FYbww6a9j__6bCxU2mdCfxUZKkG77cTgWsW7bcilQiKl6n-RkGmklLUDCbH7FylLYdIt_E4vCd2TdGWqdOGonKjPIzf03CobjUsi2UNkZ9q73ZH6AnvwQoWeVEzdshlxoDh7Hrqto2wP-9fXNQ7rrkacx_Bxm2032OGCvdeQ98Ypw_yUj0uCzhOqPt2Nil31UuwfWlEFwOqjdCnd9USMct54j1RpCSu9DODqUaL3BnW-RcGeIeFtmk3NNiQWYrw_9_WzGm7JSY7ybcSqdm3dS3Fc6xU399FKqLS0-LxlDAgHYwWMbG26PdcVs3kSNOOmgb' +
'UyqDiHTRs7samEIzhaHfpkwdN94saEBHCEIdbjFM85o0BlC8pYkqTaGiwac56JVrIY7CcQH8Bt9_N1Mg6TXT2J6oA9izCGUxzla2nbsvrh7ULKA8Z6wQtdQIr8oE_4qpK-44Gs3oONXxPG2cPbcwKYTJG2hz-n4bfssznV-PJxzX3O4vjCvomjaUwqH6sBFZQbwkmtYwEp-HheKidc-6Ap5F6_1LP0Q-cQES6O9ShAauzFYkYd8QxI4Aj8RDCHZHS596-3f4RkLh4MXmlXt-bxaJZY7vxt0NJFlw9qJfGG7HARoIcNPcU8zOfHd5TBY0iZ-Q6WA"]',

'at': 'AFoagUV4kj4oLZwRugroJvtrpNsP7p_siQ:1522496078351',
'azt': 'AFoagUWK52sk2ZSJdqSMO9kqCjMdGx8IEQ:1522496078351',
'deviceinfo': '[null,null,null,[],null,"RU",null,null,[],"GlifWebSignIn",null,[null,null,[]]]',
'gmscoreversion': 'undefined'
}

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
url = 'https://accounts.google.com/_/signup/accountdetails?hl=ru&_reqid=152552&rt=j'
req = requests.post(url, headers=headers, data=data)
print(req)