<script setup></script>

<template>
  <RouterView />

  <footer>
    <a href="/privacy">Privacy Policy</a>
    <span> | </span>
    <a href="/terms">Terms of Service</a>
  </footer>

</template>

<style scoped>
footer {
  margin-top: 60px;
  padding: 20px;
  text-align: center;
  font-size: 0.85em;
  color: #888;
  border-top: 1px solid #eee;
}
footer a {
  color: #888;
  text-decoration: none;
}
footer a:hover {
  text-decoration: underline;
}
</style>
