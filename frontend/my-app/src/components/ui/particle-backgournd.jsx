'use client'

import { useEffect, useRef } from 'react'


export function ParticleBackground() {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }
    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)

    // Particle array
    const particles= []
    const particleCount = 60 // Sparse coverage

    // Color palette - subtle purples and blues
    const colors = [
      'rgba(168, 85, 247, 0.6)',   // purple
      'rgba(139, 92, 246, 0.5)',   // purple-light
      'rgba(99, 102, 241, 0.5)',   // indigo
      'rgba(59, 130, 246, 0.4)',   // blue
    ]

    // Initialize particles
    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        size: Math.random() * 1.5 + 0.3, // Very small particles
        opacity: Math.random() * 0.4 + 0.1, // Low opacity
        baseOpacity: Math.random() * 0.4 + 0.1,
        vx: (Math.random() - 0.5) * 0.08, // Very slow movement
        vy: (Math.random() - 0.5) * 0.08,
        color: colors[Math.floor(Math.random() * colors.length)],
        wobbleSpeed: Math.random() * 0.02 + 0.005,
        wobbleAmount: Math.random() * 0.3 + 0.1,
      })
    }

    let time = 0

    // Animation loop
    const animate = () => {
      // Clear canvas completely
      ctx.fillStyle = 'rgba(13, 11, 31, 1)'
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      time += 1

      // Update and draw particles
      particles.forEach((particle) => {
        // Very subtle movement
        particle.x += particle.vx
        particle.y += particle.vy

        // Subtle wobble effect
        const wobble = Math.sin(time * particle.wobbleSpeed) * particle.wobbleAmount
        particle.opacity = particle.baseOpacity + wobble * 0.05

        // Wrap around edges smoothly
        if (particle.x < -5) particle.x = canvas.width + 5
        if (particle.x > canvas.width + 5) particle.x = -5
        if (particle.y < -5) particle.y = canvas.height + 5
        if (particle.y > canvas.height + 5) particle.y = -5

        // Draw small dust particle
        ctx.fillStyle = particle.color.replace(/[\d.]+\)/, `${particle.opacity})`)
        ctx.beginPath()
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
        ctx.fill()
      })

      requestAnimationFrame(animate)
    }

    animate()

    return () => {
      window.removeEventListener('resize', resizeCanvas)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none"
      style={{ zIndex: 0 }}
    />
  )
}
