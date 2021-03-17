<template>
  <header class="main-header">
    <!-- Header Navbar -->
    <nav class="navbar navbar-static-top" role="navigation">
      <!-- Sidebar toggle button-->
      <span class="logo-mini">
        <a href="/"><p class="center-block logo">EuroToken</p></a>
      </span>
      <!-- Navbar Right Menu -->
      <div class="navbar-custom-menu">
        <ul class="nav navbar-nav">
          <messages-menu></messages-menu>
          <notifications-menu></notifications-menu>
          <tasks-menu></tasks-menu>
          <user-menu :account="account" :accounts="accounts" :user="user"></user-menu>
        </ul>
      </div>
    </nav>
  </header>
</template>

<script>
import { mapState } from 'vuex'
import MessagesMenu from './MessagesMenu'
import NotificationsMenu from './NotificationsMenu'
import TasksMenu from './TasksMenu'
import UserMenu from './UserMenu'

export default {
  name: 'DashHeader',
  components: {
    MessagesMenu,
    NotificationsMenu,
    TasksMenu,
    UserMenu
  },
  props: ['user', 'account', 'accounts'],
  computed: {
    ...mapState([
      'userInfo'
    ])
  }
}
</script>

<style scoped>
.main-header>.navbar {
  margin-left: 0px;
}

</style>

