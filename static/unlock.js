function redirect(url){
    window.location.replace(url);
}

window.onload = function() {
    const current_url = window.location.href;
    if(!current_url.includes('timestamp')){
        const timestamp = Math.floor(Date.now() / 1000);
        var new_url = current_url + "&timestamp=" + timestamp;
        setTimeout(redirect, 100, new_url);
    }
}