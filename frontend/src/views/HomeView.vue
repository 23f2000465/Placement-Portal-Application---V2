<template>
  <div class="landing-page">
    <nav class="navbar navbar-dark landing-navbar">
      <div class="container py-2">
        <a class="navbar-brand fw-semibold" href="#home">Placement Portal</a>
        <div class="d-flex align-items-center gap-3 gap-md-4">
          <a class="nav-link text-white" href="#home">Home</a>
          <a class="nav-link text-white" href="#about">About</a>
          <a class="nav-link text-white" href="#contact">Contact</a>
          <RouterLink class="btn btn-primary px-4" to="/login">Login</RouterLink>
        </div>
      </div>
    </nav>

    <section id="home" class="hero-section py-5">
      <div class="container py-lg-5">
        <div class="row align-items-center g-5">
          <div class="col-lg-6">
            <h1 class="display-4 fw-bold mb-4">Placement Portal<br>Application V2</h1>
            <p class="lead text-secondary mb-4">
              Manage placement drives, student applications and company interactions in one simple platform.
            </p>
            <div class="d-flex flex-wrap gap-3">
              <RouterLink class="btn btn-primary btn-lg" to="/login">Login</RouterLink>
              <RouterLink class="btn btn-outline-primary btn-lg" to="/register/student">Student Register</RouterLink>
              <RouterLink class="btn btn-outline-secondary btn-lg" to="/register/company">Company Register</RouterLink>
            </div>
          </div>
          <div class="col-lg-6 text-center">
            <img src="../assets/placement-hero.png" class="img-fluid hero-image" alt="Students and company representatives using the placement portal">
          </div>
        </div>
      </div>
    </section>

    <section id="about" class="platform-section py-5 border-top">
      <div class="container py-lg-4">
        <div class="text-center mb-5">
          <h2 class="fw-bold">Our Platform</h2>
          <p class="text-secondary mb-0">A unified system for students, companies and administrators to simplify the placement process.</p>
        </div>

        <div class="row g-4">
          <div v-for="role in roles" :key="role.title" class="col-md-4">
            <div class="card h-100 border">
              <div class="card-body p-4">
                <h3 class="h4 text-center mb-4">{{ role.title }}</h3>
                <ul class="mb-0">
                  <li v-for="item in role.items" :key="item" class="mb-2">{{ item }}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <footer id="contact" class="text-center py-4 border-top bg-light text-secondary">
      © 2026 Placement Portal Application V2. All rights reserved.
    </footer>
  </div>
</template>

<script setup>
const roles = [
  {
    title: 'Admin',
    items: ['Approve companies and drives', 'Manage users and blacklist', 'View placement statistics', 'Generate reports'],
  },
  {
    title: 'Company',
    items: ['Register and manage company profile', 'Create and manage placement drives', 'View and shortlist applicants', 'Schedule interviews'],
  },
  {
    title: 'Student',
    items: ['Register and build profile', 'Browse and apply to drives', 'Track application status', 'View interview schedules'],
  },
]
</script>

<style scoped>
.landing-page {
  color: #172033;
  background: white;
}

.landing-navbar {
  background: #101b2d;
}

.hero-section {
  min-height: 560px;
  display: flex;
  align-items: center;
}

.hero-image {
  max-height: 500px;
  object-fit: contain;
}

.platform-section {
  scroll-margin-top: 20px;
}

.card {
  box-shadow: 0 2px 8px rgba(23, 32, 51, 0.06);
}

@media (max-width: 767px) {
  .landing-navbar .container {
    justify-content: center;
    gap: 10px;
  }

  .landing-navbar .nav-link {
    display: none;
  }

  .hero-section {
    min-height: auto;
    text-align: center;
  }

  .hero-section .d-flex {
    justify-content: center;
  }
}
</style>
