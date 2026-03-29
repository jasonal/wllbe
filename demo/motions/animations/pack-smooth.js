window.MotionPackSmooth = {
    name: "smooth",
    apply: function(tl, el, type, config) {
        // Enforce visible state for animation start
        gsap.set(el, { opacity: 1 }); // Resets the potential opacity: 0 from preparation
        
        switch(type) {
            case 'fade-up':
                tl.from(el, { y: 40, opacity: 0, duration: 1.2, ease: 'power2.out' }, config.position);
                break;
            case 'fade-in':
                tl.from(el, { opacity: 0, duration: 1.5, ease: 'power1.inOut' }, config.position);
                break;
            case 'zoom-in':
                tl.from(el, { scale: 0.95, opacity: 0, duration: 1.2, ease: 'power2.out' }, config.position);
                break;
            case 'stagger-up':
                // For nested children, we need special handling
                gsap.set(el.children, { opacity: 1 }); 
                tl.from(el.children, { y: 30, opacity: 0, duration: 1, ease: 'power2.out', stagger: 0.15 }, config.position);
                break;
        }
    }
};
