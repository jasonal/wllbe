window.MotionTransitions = {
    fade: function(nextSlide, prevSlide, direction) {
        const tl = gsap.timeline();
        if (prevSlide) tl.to(prevSlide, { opacity: 0, scale: 0.95, duration: 0.6, ease: "power2.inOut" });
        tl.fromTo(nextSlide, 
            { opacity: 0, scale: 1.05, display: 'none' }, 
            { opacity: 1, scale: 1, display: 'flex', duration: 0.8, ease: "power2.out" }, "-=0.4"
        );
        return tl;
    },
    slide: function(nextSlide, prevSlide, direction) {
        const tl = gsap.timeline();
        const xOffset = direction > 0 ? 100 : -100;
        if (prevSlide) tl.to(prevSlide, { xPercent: -xOffset, opacity: 0, duration: 0.6, ease: "power2.in" });
        tl.fromTo(nextSlide, 
            { xPercent: xOffset, opacity: 0, display: 'none' }, 
            { xPercent: 0, opacity: 1, display: 'flex', duration: 0.8, ease: "power2.out" }, "-=0.4"
        );
        return tl;
    },
    zoom: function(nextSlide, prevSlide, direction) {
        const tl = gsap.timeline();
        if (prevSlide) tl.to(prevSlide, { scale: 1.5, opacity: 0, duration: 0.7, ease: "power2.in" });
        tl.fromTo(nextSlide, 
            { scale: 0.5, opacity: 0, display: 'none' }, 
            { scale: 1, opacity: 1, display: 'flex', duration: 0.8, ease: "back.out(1.2)" }, "-=0.5"
        );
        return tl;
    },
    flip: function(nextSlide, prevSlide, direction) {
        const tl = gsap.timeline();
        const rotate = direction > 0 ? 90 : -90;
        if (prevSlide) tl.to(prevSlide, { rotateY: -rotate, opacity: 0, duration: 0.7, ease: "power2.inOut" });
        tl.fromTo(nextSlide, 
            { rotateY: rotate, opacity: 0, display: 'none' }, 
            { rotateY: 0, opacity: 1, display: 'flex', duration: 0.8, ease: "power2.out" }, "-=0.5"
        );
        return tl;
    },
    convex: function(nextSlide, prevSlide, direction) {
        const tl = gsap.timeline();
        const yOffset = direction > 0 ? 100 : -100;
        if (prevSlide) tl.to(prevSlide, { yPercent: -yOffset * 0.3, opacity: 0, duration: 0.6, ease: "power2.in" });
        tl.fromTo(nextSlide, 
            { yPercent: yOffset, opacity: 0, display: 'none' }, 
            { yPercent: 0, opacity: 1, display: 'flex', duration: 0.8, ease: "power2.out" }, "-=0.4"
        );
        return tl;
    }
};
