<template>
  <li class="dropdown user user-menu">
    <a href="javascript:;" class="dropdown-toggle" data-toggle="dropdown">
      <!-- The user image in the navbar-->
      <img :src="user.avatar" class="user-image" alt="User Image">
      <!-- hidden-xs hides the username on small devices so only the image appears. -->
      <span class="hidden-xs">{{store.account}}</span>
    </a>
    <!-- Account Info and Menu -->
    <ul class="dropdown-menu">
      <li class="user-header" style="height:auto;min-height:85px;padding-bottom:15px;">
        <p>
          <span>{{user.displayName}}</span>
          <small v-for="role in user.roles" :key="role">{{role}}</small>
        </p>
      </li>
      <li>
        <div class="col-xs-12">
          <div class="form-group">
            <label>Select Wallet Account</label>
            <select v-model="store.account" class="form-control">
              <option v-for="acc in accounts">{{acc}}</option>
            </select>
          </div>
        </div>
      </li>
      <li class="user-footer">
        <a href="javascript:;" class="btn btn-default btn-flat btn-block">
          <i class="fa fa-sign-out"></i>
          <span>Logout</span>
        </a>
      </li>
    </ul>
  </li>
</template>

<script>
const stores = require('../shared_state.js')
export default {
  name: 'UserMenu',
  props: ['user', 'account', 'accounts'],
  data: function() {
    return {
      store: stores.store.state
    }
  },
  methods: {
    changeAccount(event) {
      console.log('kek')
      Event.$emit('account-change', event.target.value)
    }
  }

}
</script>
