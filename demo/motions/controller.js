class MotionController {
  constructor() {
    this.enableAnimations = true;
    this.enableTransitions = true;
    this.timelines = [];
    this.currentPack = window.MotionPackSmooth;
    this.currentTransition = window.MotionTransitions.fade;
  }

  setPack(packObject) {
    this.currentPack = packObject;
    this.replay();
  }

  setTransition(transitionFn) {
    this.currentTransition = transitionFn;
  }

  toggleAnimations(enable) {
    this.enableAnimations = enable;
    if (!enable) this.clearAnimations();
    else this.playAnimations();
  }

  toggleTransitions(enable) {
    this.enableTransitions = enable;
  }

  clearAnimations() {
    this.timelines.forEach(tl => tl.kill());
    this.timelines = [];
    const elements = document.querySelectorAll('[data-motion]');
    // Clean all GSAP generated inline styles
    gsap.set(elements, { clearProps: 'all' });
  }

  /**
   * IMPORTANT: Prepare the slide for entrance animation.
   * If animations are ENABLED, hide all [data-motion] elements immediately.
   */
  prepareSlide(slide) {
    if (!this.enableAnimations) return;
    const elements = slide.querySelectorAll('[data-motion]');
    gsap.set(elements, { opacity: 0, visibility: 'hidden' });
  }

  playAnimations() {
    if (!this.enableAnimations) return;
    this.clearAnimations();

    const activeSlide = document.querySelector('.l-slide.active');
    if (!activeSlide) return;

    const elements = activeSlide.querySelectorAll('[data-motion]');
    elements.forEach(el => {
        const type = el.getAttribute('data-motion');
        const delay = parseFloat(el.getAttribute('data-delay')) || 0;
        const tl = gsap.timeline({});
        this.timelines.push(tl);

        // Before animating, ensure it is VISIBLE but still opacity 0 (reset 'hidden' from prepare)
        gsap.set(el, { visibility: 'visible' });

        if (this.currentPack && this.currentPack.apply) {
            this.currentPack.apply(tl, el, type, { position: delay / 1000 });
        }
    });
  }

  replay() {
    this.playAnimations();
  }

  // Handle Switch with optional transition
  async transitionTo(nextSlide, prevSlide, direction) {
    if (this.enableTransitions && this.currentTransition) {
        return this.currentTransition(nextSlide, prevSlide, direction);
    } else {
        if (prevSlide) prevSlide.style.display = 'none';
        nextSlide.style.display = 'flex';
        return Promise.resolve();
    }
  }
}

window.motionController = new MotionController();
