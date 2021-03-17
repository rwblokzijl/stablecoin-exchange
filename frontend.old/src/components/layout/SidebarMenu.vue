<template>
  <ul class="sidebar-menu">

    <li class="header">As a User</li>
    <router-link tag="li" class="pageLink" to="/account">
      <a>
      <i class="fa fa-money"></i>
        <span class="page">Wallet</span>
      </a>
    </router-link>
    <router-link tag="li" class="pageLink" to="/transactions">
      <a>
        <i class="fa fa-th-list"></i>
        <span class="page">Transactions</span>
      </a>
    </router-link>
    <router-link tag="li" class="pageLink" to="/exchange">
      <a>
        <i class="fa fa-exchange"></i>
        <span class="page">Exchange</span>
      </a>
    </router-link>

    <li class="header">As a central bank</li>
    <router-link tag="li" class="pageLink" to="/bank">
      <a>
        <i class="fa fa-bank"></i>
        <span class="page">Dashboard</span>
      </a>
    </router-link>
    <router-link tag="li" class="pageLink" to="/bank/policy">
      <a>
        <i class="fa fa-book"></i>
        <span class="page">Policy</span>
      </a>
    </router-link>
    <router-link tag="li" class="pageLink" to="/bank/statistics/">
      <a>
        <i class="fa fa-line-chart"></i>
        <span class="page">Statistics</span>
      </a>
    </router-link>

    <li class="header">As a regulator</li>
    <router-link tag="li" class="pageLink" to="/regulator">
      <a>
        <i class="fa fa-desktop"></i>
        <span class="page">Dashboard</span>
      </a>
    </router-link>
    <router-link tag="li" class="pageLink" to="/regulator/cases">
      <a>
        <i class="fa fa-files-o"></i>
        <span class="page">Cases</span>
      </a>
    </router-link>

    <li class="header">As a notary</li>
    <router-link tag="li" class="pageLink" to="/notary">
      <a>
        <i class="fa fa-user"></i>
        <span class="page">Dashboard</span>
      </a>
    </router-link>
    <router-link tag="li" class="pageLink" to="/notary/requests">
      <a>
        <i class="fa fa-question"></i>
        <span class="page">Confirmation requests</span>
      </a>
    </router-link>
    <router-link tag="li" class="pageLink" to="/notary/statistics">
      <a>
        <i class="fa fa-line-chart"></i>
        <span class="page">Statistics</span>
      </a>
    </router-link>

  </ul>
</template>
<script>
export default {
  name: 'SidebarMenu'
}
</script>
<style>
/* override default */
.sidebar-menu > li > a {
  padding: 12px 15px 12px 15px;
}

.sidebar-menu li.active > a > .fa-angle-left,
.sidebar-menu li.active > a > .pull-right-container > .fa-angle-left {
  animation-name: rotate;
  animation-duration: 0.2s;
  animation-fill-mode: forwards;
}

.treeview-title {
  z-index: 1;
}

@keyframes rotate {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(-90deg);
  }
}
</style>
