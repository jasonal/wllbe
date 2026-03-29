window.MotionPackBouncy = {
    name: "bouncy",
    apply: function(tl, el, type, config) {
        gsap.set(el, { opacity: 1 });

        switch(type) {
            case 'fade-up':
                tl.from(el, { y: 100, opacity: 0, duration: 1, ease: 'back.out(1.7)' }, config.position);
                break;
            case 'fade-in':
                tl.from(el, { scale: 0.8, opacity: 0, duration: 0.8, ease: 'back.out(2)' }, config.position);
                break;
            case 'zoom-in':
                tl.from(el, { scale: 0.4, opacity: 0, duration: 1.2, ease: 'elastic.out(1, 0.5)' }, config.position);
                break;
            case 'stagger-up':
                gsap.set(el.children, { opacity: 1 });
                tl.from(el.children, { y: 60, opacity: 0, duration: 0.8, ease: 'back.out(1.5)', stagger: 0.1 }, config.position);
                break;
        }
    }
};
