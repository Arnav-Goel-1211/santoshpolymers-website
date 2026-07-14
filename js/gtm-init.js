window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
var consentState = localStorage.getItem('cookie-consent') === 'granted' ? 'granted' : 'denied';
gtag('consent', 'default', {
  'ad_storage': consentState,
  'ad_user_data': consentState,
  'ad_personalization': consentState,
  'analytics_storage': consentState
});
gtag('js', new Date());
gtag('config', 'G-XHS7WCSSHB');
