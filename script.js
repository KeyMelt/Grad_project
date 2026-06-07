// script.js
document.addEventListener("DOMContentLoaded", () => {
  // IntersectionObserver fallback for browsers that don't support scroll-driven animations
  if (!CSS.supports('(animation-timeline: view()) and (animation-range: entry)')) {
    const animatedElements = document.querySelectorAll('.animated-element');
    
    // Add hidden state class initially
    animatedElements.forEach(el => el.classList.add('io-hidden'));

    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.remove('io-hidden');
          entry.target.classList.add('io-visible');
          obs.unobserve(entry.target); // Only animate once
        }
      });
    }, {
      root: null,
      threshold: 0.1, // Trigger when 10% of the element is visible
      rootMargin: "0px 0px -50px 0px"
    });

    animatedElements.forEach(el => {
      observer.observe(el);
    });
  }

  // --- Canvas Grid Animation ---
  const canvas = document.getElementById('grid-canvas');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    let width, height;
    let cols, rows;
    let h_edges, v_edges;
    let rects = [];
    let cameraY = 0;
    const gridSize = 40;
    const speed = 0.8;
    
    function initGrid() {
      cols = Math.ceil(width / gridSize);
      rows = 3000;
      
      h_edges = new Uint8Array(cols * (rows + 1));
      v_edges = new Uint8Array((cols + 1) * rows);
      rects = [];
      
      for(let i = 0; i < cols; i++) {
        h_edges[i] = 1;
        h_edges[i + rows * cols] = 1;
      }
      for(let i = 0; i < rows; i++) {
        v_edges[0 + i * (cols + 1)] = 1;
        v_edges[cols + i * (cols + 1)] = 1;
      }
      
      function split(rx, ry, rw, rh) {
        if (rw <= 2 && rh <= 2) {
          rects.push({x: rx, y: ry, w: rw, h: rh});
          return;
        }
        if (Math.random() < 0.15 && rw <= 4 && rh <= 4) {
          rects.push({x: rx, y: ry, w: rw, h: rh});
          return;
        }
        
        let splitH = false;
        if (rw > rh * 1.5) splitH = false;
        else if (rh > rw * 1.5) splitH = true;
        else splitH = Math.random() > 0.5;
        
        if (splitH && rh >= 2) {
          let minCut = 1;
          let maxCut = rh - 1;
          let cut = minCut + Math.floor(Math.random() * (maxCut - minCut + 1));
          
          for(let i = 0; i < rw; i++) h_edges[(rx + i) + (ry + cut) * cols] = 1;
          
          split(rx, ry, rw, cut);
          split(rx, ry + cut, rw, rh - cut);
        } else if (!splitH && rw >= 2) {
          let minCut = 1;
          let maxCut = rw - 1;
          let cut = minCut + Math.floor(Math.random() * (maxCut - minCut + 1));
          
          for(let i = 0; i < rh; i++) v_edges[(rx + cut) + (ry + i) * (cols + 1)] = 1;
          
          split(rx, ry, cut, rh);
          split(rx + cut, ry, rw - cut, rh);
        } else {
           rects.push({x: rx, y: ry, w: rw, h: rh});
        }
      }
      
      split(0, 0, cols, rows);
      cameraY = rows * gridSize - height - 1000;
    }
    
    function resize() {
      const rect = canvas.getBoundingClientRect();
      width = rect.width;
      height = rect.height;
      canvas.width = width * 1.5;
      canvas.height = height * 1.5;
      ctx.scale(1.5, 1.5);
      initGrid();
    }
    
    window.addEventListener('resize', resize);
    resize();

    const colors = ['#00C9A7', '#F5A623', '#00C9A7'];
    const numTracers = 25;
    const tracers = [];
    const pulses = [];
    const sparks = [];

    class Tracer {
      constructor() {
        this.reset();
        let visibleGridY = Math.floor(cameraY / gridSize) + Math.floor(Math.random() * (height / gridSize));
        this.gridY = Math.max(0, Math.min(rows, visibleGridY));
        this.pixelY = this.gridY * gridSize;
        this.history = [{x: this.pixelX, y: this.pixelY}];
      }
      
      reset() {
        this.gridX = Math.floor(Math.random() * cols);
        let startY = Math.floor(cameraY / gridSize) - 5;
        if (startY < 0) startY = 0;
        this.gridY = startY + Math.floor(Math.random() * 15);
        if (this.gridY > rows) this.gridY = rows;
        
        this.history = [];
        this.length = Math.floor(Math.random() * 100) + 40; 
        this.color = colors[Math.floor(Math.random() * colors.length)];
        this.pixelX = this.gridX * gridSize;
        this.pixelY = this.gridY * gridSize;
        this.moveSpeed = 3;
        this.dir = -1;
        this.pickDirection();
        
        this.history.push({x: this.pixelX, y: this.pixelY});
      }
      
      getValidDirs() {
        let x = this.gridX, y = this.gridY;
        let dirs = [];
        if (y > 0 && v_edges[x + (y - 1) * (cols + 1)]) dirs.push(0); // UP
        if (x < cols && h_edges[x + y * cols]) dirs.push(1); // RIGHT
        if (y < rows && v_edges[x + y * (cols + 1)]) dirs.push(2); // DOWN
        if (x > 0 && h_edges[(x - 1) + y * cols]) dirs.push(3); // LEFT
        return dirs;
      }
      
      pickDirection() {
        let dirs = this.getValidDirs();
        if (dirs.length === 0) {
          this.dir = -1;
          return;
        }
        if (this.dir !== -1 && dirs.includes(this.dir) && Math.random() < 0.75) {
          // Keep straight
        } else {
          let forwardDirs = dirs.filter(d => d !== (this.dir + 2) % 4);
          if (forwardDirs.length > 0) {
            this.dir = forwardDirs[Math.floor(Math.random() * forwardDirs.length)];
          } else {
            this.dir = dirs[Math.floor(Math.random() * dirs.length)];
          }
        }
      }
      
      update() {
        if (this.dir === -1) {
          this.reset();
          return;
        }
        
        let targetX = this.gridX * gridSize;
        let targetY = this.gridY * gridSize;
        
        if (this.dir === 0) targetY -= gridSize;
        else if (this.dir === 1) targetX += gridSize;
        else if (this.dir === 2) targetY += gridSize;
        else if (this.dir === 3) targetX -= gridSize;
        
        if (this.dir === 0) this.pixelY -= this.moveSpeed;
        else if (this.dir === 1) this.pixelX += this.moveSpeed;
        else if (this.dir === 2) this.pixelY += this.moveSpeed;
        else if (this.dir === 3) this.pixelX -= this.moveSpeed;
        
        this.history.unshift({x: this.pixelX, y: this.pixelY});
        if (this.history.length > this.length / this.moveSpeed) {
          this.history.pop();
        }
        
        let reached = false;
        if (this.dir === 0 && this.pixelY <= targetY) { this.pixelY = targetY; reached = true; }
        if (this.dir === 1 && this.pixelX >= targetX) { this.pixelX = targetX; reached = true; }
        if (this.dir === 2 && this.pixelY >= targetY) { this.pixelY = targetY; reached = true; }
        if (this.dir === 3 && this.pixelX <= targetX) { this.pixelX = targetX; reached = true; }
        
        if (reached) {
          if (this.dir === 0) this.gridY--;
          else if (this.dir === 1) this.gridX++;
          else if (this.dir === 2) this.gridY++;
          else if (this.dir === 3) this.gridX--;
          
          let oldDir = this.dir;
          this.pickDirection();
          
          // Generate spark on turn
          if (oldDir !== this.dir) {
            sparks.push({x: this.pixelX, y: this.pixelY, life: 1.0, color: this.color});
          }
        }
      }
      
      draw() {
        if (this.history.length < 2) return;
        
        let headScreenY = this.history[0].y - cameraY;
        if (headScreenY > height + 400 || headScreenY < -400) {
          this.reset();
          return;
        }
        
        ctx.beginPath();
        ctx.moveTo(this.history[0].x, this.history[0].y - cameraY);
        for (let i = 1; i < this.history.length; i++) {
          ctx.lineTo(this.history[i].x, this.history[i].y - cameraY);
        }
        
        ctx.strokeStyle = this.color;
        ctx.lineWidth = 4;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.shadowBlur = 15;
        ctx.shadowColor = this.color;
        ctx.stroke();
        ctx.shadowBlur = 0;
      }
    }

    for (let i = 0; i < numTracers; i++) {
      tracers.push(new Tracer());
    }

    function animate() {
      ctx.clearRect(0, 0, width, height);
      cameraY -= speed;
      if (cameraY < 0) cameraY = rows * gridSize - height - 1000;

      // Draw faint base grid lines
      ctx.beginPath();
      ctx.strokeStyle = 'rgba(0, 201, 167, 0.15)';
      ctx.lineWidth = 1;
      
      let startY = Math.max(0, Math.floor(cameraY / gridSize));
      let endY = Math.min(rows, Math.ceil((cameraY + height) / gridSize) + 5);
      
      for(let y = startY; y <= endY; y++) {
        for(let x = 0; x < cols; x++) {
          if (h_edges[x + y * cols]) {
            ctx.moveTo(x * gridSize, y * gridSize - cameraY);
            ctx.lineTo((x + 1) * gridSize, y * gridSize - cameraY);
          }
        }
      }
      
      for(let x = 0; x <= cols; x++) {
        for(let y = startY; y < endY; y++) {
          if (v_edges[x + y * (cols + 1)]) {
            ctx.moveTo(x * gridSize, y * gridSize - cameraY);
            ctx.lineTo(x * gridSize, (y + 1) * gridSize - cameraY);
          }
        }
      }
      ctx.stroke();
      
      // Spawn data pulses randomly
      if (Math.random() < 0.05) {
        let visibleRects = rects.filter(r => r.y >= startY && r.y + r.h <= endY);
        if (visibleRects.length > 0) {
          let r = visibleRects[Math.floor(Math.random() * visibleRects.length)];
          pulses.push({
            rect: r,
            life: 1.0,
            color: colors[Math.floor(Math.random() * colors.length)]
          });
        }
      }

      // Draw Pulses
      for (let i = pulses.length - 1; i >= 0; i--) {
        let p = pulses[i];
        p.life -= 0.015;
        if (p.life <= 0) {
          pulses.splice(i, 1);
          continue;
        }
        ctx.save();
        ctx.globalAlpha = p.life * 0.12; // Max opacity 12%
        ctx.fillStyle = p.color;
        ctx.fillRect(p.rect.x * gridSize, p.rect.y * gridSize - cameraY, p.rect.w * gridSize, p.rect.h * gridSize);
        ctx.restore();
      }

      // Draw Sparks
      for (let i = sparks.length - 1; i >= 0; i--) {
        let s = sparks[i];
        s.life -= 0.04;
        if (s.life <= 0) {
          sparks.splice(i, 1);
          continue;
        }
        ctx.beginPath();
        ctx.arc(s.x, s.y - cameraY, 1 + s.life * 3, 0, Math.PI * 2);
        ctx.fillStyle = s.color;
        ctx.shadowBlur = 10;
        ctx.shadowColor = s.color;
        ctx.globalAlpha = s.life;
        ctx.fill();
        ctx.globalAlpha = 1.0;
        ctx.shadowBlur = 0;
      }

      tracers.forEach(t => {
        t.update();
        t.draw();
      });

      requestAnimationFrame(animate);
    }
    animate();
  }
});
