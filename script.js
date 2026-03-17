document.addEventListener('DOMContentLoaded', () => {

    // --- Modal Logic ---
    const modal = document.getElementById('waitlistModal');
    const openBtns = document.querySelectorAll('.open-modal');
    const closeBtn = document.getElementById('closeModal');
    const form = document.getElementById('leadForm');
    const submitBtn = document.getElementById('submitBtn');

    // Open Modal
    openBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            modal.classList.add('active');
            document.body.style.overflow = 'hidden'; // Prevent background scrolling
        });
    });

    // Close Modal via Button
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            closeModal();
        });
    }

    // Close Modal via Background Click
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });
    }

    function closeModal() {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto'; // Restore scrolling
    }

    // --- Form Submission Logic ---
    if(form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const name = document.getElementById('name').value;
            const phone = document.getElementById('phone').value;
            const email = document.getElementById('email').value;
            
            if(name && phone && email) {
                const originalText = submitBtn.textContent;
                submitBtn.textContent = 'JOINING WAITLIST...';
                submitBtn.style.opacity = '0.8';
                submitBtn.disabled = true;

                // 1. Send to Discord Webhook
                const discordWebhookUrl = 'https://discord.com/api/webhooks/1483319787697475594/0iUoNd0bjT7wX6xX2feZNRV1qmV6vTv-UVjNmSYpPCgGOTkW2UyZms75h9PzHv1kO7Lt';
                const discordPayload = {
                    embeds: [{
                        title: "🚀 New Waitlist Lead!",
                        color: 0x00f2fe,
                        fields: [
                            { name: "Name", value: name, inline: true },
                            { name: "Phone", value: phone, inline: true },
                            { name: "Email", value: email, inline: false }
                        ],
                        timestamp: new Date()
                    }]
                };

                try {
                    // Send to Discord
                    await fetch(discordWebhookUrl, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(discordPayload)
                    });

                    // 2. Send to Formspree
                    const formspreeUrl = 'https://formspree.io/f/mdawpnnq';
                    const formspreeData = new FormData();
                    formspreeData.append('name', name);
                    formspreeData.append('phone', phone);
                    formspreeData.append('email', email);

                    await fetch(formspreeUrl, {
                        method: 'POST',
                        body: formspreeData,
                        headers: {
                            'Accept': 'application/json'
                        }
                    });

                    // Success Feedback
                    submitBtn.textContent = 'YOU ARE ON THE LIST!';
                    submitBtn.style.background = '#2e7d32'; 
                    submitBtn.style.color = '#fff';
                    
                    setTimeout(() => {
                        form.reset();
                        submitBtn.textContent = originalText;
                        submitBtn.style.background = 'linear-gradient(135deg, #00f2fe, #4facfe)';
                        submitBtn.style.color = '#000';
                        submitBtn.style.opacity = '1';
                        submitBtn.disabled = false;
                        closeModal();
                    }, 2000);

                } catch (error) {
                    console.error('Error submitting form:', error);
                    submitBtn.textContent = 'ERROR! TRY AGAIN';
                    submitBtn.style.background = '#d32f2f';
                    submitBtn.disabled = false;
                    setTimeout(() => {
                        submitBtn.textContent = originalText;
                        submitBtn.style.background = 'linear-gradient(135deg, #00f2fe, #4facfe)';
                    }, 3000);
                }
            }
        });
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if(target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});
