var dots_on = 0;
let slide_images = document.getElementsByClassName('slideshow');
var last_image_id = 0;

function reload() {
    var city_name = document.getElementById("city_name").value;
    var address = window.location.protocol + "//" + window.location.hostname + ":" + window.location.port  + window.location.pathname + "?city_name=" + city_name;
    location.href = address;
}

function setupVideoQueue(start_id, end_id){
    var startVideo = document.getElementById(start_id);
    var endVideo = document.getElementById(end_id);

    var duration = (startVideo.duration / startVideo.playbackRate - 2) * 1000;

    startVideo.classList.add('showing');
    startVideo.classList.remove('fading');
    endVideo.classList.add('fading');
    endVideo.classList.remove('showing');

    startVideo.currentTime = 0;

    setTimeout(() => {
        startVideo.classList.remove('showing');
        startVideo.classList.add('fading');
        endVideo.classList.remove('fading');
        endVideo.classList.add('showing');
        endVideo.play();
    }, duration)
}

function adjust_time(){
    var dots = document.getElementById("dots");
    var hours = document.getElementById("hours");
    var minutes = document.getElementById("minutes");
    var current = new Date();
    var hour_str = "0" + current.getHours();
    var minute_str = "0" + current.getMinutes();
    hours.textContent = hour_str.slice(-2);
    minutes.textContent = minute_str.slice(-2);

    if(dots_on > 0){
        dots_on = 0;
        dots.style.opacity = "0.2";
    }else{
        dots_on = 1;
        dots.style.opacity = "1";
    }
}

function update_slideshow(){
    if (last_image_id < slide_images.length){
        slide_images[last_image_id].style.opacity = 1;
        last_image_id ++;
    }else{
        last_image_id = 0;
        setupVideoQueue('video_1', 'video_2');

        const count = slide_images.length;
        for (let i = 0; i < count; i++) {
            slide_images[i].style.opacity = 0;
        }
    }
}

function start_slideshow(){
    const count = slide_images.length;

    if(count > 0){
        for (let i = 0; i < count; i++) {
            slide_images[i].style.opacity = 0;
            slide_images[i].style.zIndex = 10 + i;
        }

        setInterval(update_slideshow, 15000);
    }
}

window.onload = function() {
    // Refresh every half an hour
    setTimeout(reload, 1800000);
    setInterval(adjust_time, 1000);
    start_slideshow();
}