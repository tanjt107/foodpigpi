## Intoduction
This package is used for order management for online shops.

## Collect Order Information
This example uses Google Form to accept order. Form responses are then exported to Google Sheets[^1]. Data is hence extracted using Google Sheets API and transformed.

## Notification and Whatsapp link
Order confirmation notifications based on provided template with emojis are created for each user. Links to Whatsapp which include pre-filed message are created.[^2]. Below is an example of template and the notification.

```jinja
ðð½FOODPIGPI è²æè¨å®ç¢ºèªå®ð¥¯
Helloðð»ââï¸å¤è¬ä½ æ¯æðð¤ð¤
ä½ è¨äº

{% for shop, categories in items_by_shop.items() %}
{{ shop }}
{% for category, items in categories.items() %}
{{ category }}
{% for item, quantity in items.items() %}
{{ item }} x {{ quantity }}
{% endfor %}
{% endfor %}
{% endfor %}

ðð½äº¤æ¶æéä¿ðð½
{% for delivery in delivery_options.values() %}
{{ delivery }}
{% endfor %}

ðð»TOTAL : {{ price }}
ðð»â­â­ç¢ºèªè¨å®å¾ éº»ç©å¿é åå³ä¿¡æ¯ç¢ºèªâ­â­
ðð»æ­¤çºæå¾ç¢ºèªå®â ï¸
å¦msgå§æ²æååºçé ç®è¡¨ç¤ºæ»¿äºåå¦ï½
```

![IMG_0627](https://user-images.githubusercontent.com/71891904/154886905-816c0d1b-39dd-4f8e-8dc2-7933c407411b.jpg)

## Other features
Multiple reports of spreadsheets are also created for order management.


[^1]: [View & manage form responses](https://support.google.com/docs/answer/139706?hl=en&ref_topic=6063592#zippy=%2Cdownload-all-responses-as-a-csv-file%2Cview-all-responses-in-a-spreadsheet)
[^2]: [How to link to WhatsApp from a different app](https://faq.whatsapp.com/iphone/how-to-link-to-whatsapp-from-a-different-app/?lang=en)
