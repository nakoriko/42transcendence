<script></script>
<template>
    <div class="legal-page">
        <h1>Privacy Policy</h1>
        <p class="updated">Last update: June 2026</p>

        <section>
            <h2>1. What daat we collect</h2>
             <p>We collect your email address and username when you register. During gameplay we record match results, scores, and reaction times.</p>
        </section>

        <section>
            <h2>2. How we use your data</h2>
            <p>Your data is used solely to provide game functionality: authentication, match history, leaderboards, and analytics dashboards.</p>
        </section>

        <section>
            <h2>3. Data storage</h2>
            <p>All data is stored in a PostgreSQL database running locally in a Docker container. No data is shared with third parties.</p>
        </section>

        <section>
            <h2>4. Your rights</h2>
            <p>You can request deletion of your account and all associated data at any time by contacting the platform administrator.</p>
        </section>
    </div>
</template>

<style scoped>
.legal-page {
  max-width: 800px;
  margin: 40px auto;
  padding: 0 20px;
  line-height: 1.7;
}
.updated {
  color: #888;
  font-size: 0.9em;
}
h2 {
  margin-top: 2em;
}
</style>