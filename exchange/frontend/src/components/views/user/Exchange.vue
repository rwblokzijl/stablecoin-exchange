<template>
  <!-- Main content -->
  <section class="content">
    <!-- GitHub hint -->
    <div class="row justify-content-center">

      <!-- Info boxes -->
      <div class="col-md-3 col-sm-6 col-xs-12">
        <info-box color-class="bg-green"
                  :icon-classes="['fa', 'fa-plus']"
                  text="Euro -> Eurotoken"
                  v-bind:number="'1.00€ -> ' + rateE2T + 'ET'"></info-box>
      </div>
      <!-- /.col -->
      <div class="col-md-3 col-sm-6 col-xs-12">
        <info-box color-class="bg-blue"
                  :icon-classes="['fa', 'fa-minus']"
                  text="Eurotoken -> Euro"
                  v-bind:number="'1.00ET -> ' + rateT2E + '€'"></info-box>
      </div>
      <!-- /.col -->
    </div>
    <div class="row justify-content-center">
      <!-- fix for small devices only -->
      <div class="clearfix visible-sm-block"></div>

      <!-- /.col -->
      <div class="col-md-3 col-sm-6 col-xs-12">
        <info-box color-class="bg-yellow"
                  :icon-classes="['fa', 'fa-money']"
                  text="Token Balance"
                  v-bind:number="balance.toLocaleString() + 'ET'"></info-box>
      </div>
      <!-- /.col -->
    </div>
    <!-- /.row -->

    <div class="row">
      <div class="col-xs-12">
        <h2>Euro -> Eurotoken</h2>
      </div>
      <!-- with characthers -->
      <div class="col-md-6 col-xs-12">
        <label>Amount (Euro)</label>
        <div class="input-group">
          <span class="input-group-addon">
            <i class="fa fa-fw fa-eur" aria-hidden="true" ></i>
          </span>
          <input v-on:keyup.enter="initExchangeE2T" class="form-control" v-model="exchangeAmountE2T" type="text"
          placeholder="0.00" @keypress="onlyForCurrencyE2T" >
          <span class="input-group-addon"> : {{exchangeAmountE2TConverted}}ET</span>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-md-6 col-xs-12">
        <div class="form-group">
          <label>Payment Method</label>
          <select class="form-control">
            <option>Ideal</option>
            <option>option 2</option>
            <option>option 3</option>
            <option>option 4</option>
            <option>option 5</option>
          </select>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-md-6 col-xs-12">
        <a v-on:click="initExchangeE2T" class="btn btn-primary" role="button">Convert</a>
      </div>
    </div>

    <div class="row">
      <div class="col-xs-12">
        <h2>Eurotoken -> Euro</h2>
      </div>
      <!-- with characthers -->
      <div class="col-md-6 col-xs-12">
        <label>Amount (EuroToken)</label>
        <div class="input-group">
          <span class="input-group-addon">
            <i class="fa fa-fw fa-money" aria-hidden="true" ></i>
          </span>
          <input v-on:keyup.enter="initExchangeT2E" class="form-control" v-model="exchangeAmountT2E" type="text"
          placeholder="0.00" @keypress="onlyForCurrencyT2E" >
          <span class="input-group-addon"> : € {{exchangeAmountT2EConverted}}</span>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-md-6 col-xs-12">
        <div class="form-group">
          <label>IBAN</label>
          <input class="form-control" placeholder="NL91 ABNA 0417 1643 00" type="text">
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-md-6 col-xs-12">
        <a v-on:click="initExchangeT2E" class="btn btn-primary" role="button">Convert</a>
      </div>
    </div>

    <div class="col-xs-12">
      <h2>Exchange History</h2>
    </div>

    <div class="row">
      <div class="col-md-6 col-xs-12 table-responsive">
        <table
          role="grid"
          id="example1"
          class="table table-bordered table-striped dataTable">
          <thead>
            <tr role="row">
              <th style="width: 167px;" colspan="1" rowspan="1" tabindex="0">Created</th>
              <th style="width: 182px;" colspan="1" rowspan="1" tabindex="0">Amount</th>
              <th style="width: 142px;" colspan="1" rowspan="1" tabindex="0">Paid</th>
              <th style="width: 101px;" colspan="1" rowspan="1" tabindex="0">ID</th>
              <th style="width: 101px;" colspan="1" rowspan="1" tabindex="0">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="transaction in transactions" class="even" role="row">
              <td>{{transaction.created_on}}</td>
              <td>{{centToWhole(transaction.payout_amount)}} {{transaction.payout_currency}}</td>
              <td>{{centToWhole(transaction.amount)}} {{transaction.payment_currency}}</td>
              <td>{{transaction.payment_id}}</td>
              <td>
                <a :disabled="transaction.status != 1 " v-on:click="confirmTransaction(transaction.payment_id,
                                                       transaction.counterparty_account)" class="btn btn-primary" role="button">
                  {{transaction.status_text}}
                </a>
              </td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <th colspan="1" rowspan="1">Created</th>
              <th colspan="1" rowspan="1">Amount</th>
              <th colspan="1" rowspan="1">Paid</th>
              <th colspan="1" rowspan="1">ID</th>
              <th colspan="1" rowspan="1">Status</th>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
    <!-- /.row -->
  </section>
  <!-- /.content -->
</template>

<script>
import Alert from '../../widgets/Alert'
import InfoBox from '../../widgets/InfoBox'
import ProcessInfoBox from '../../widgets/ProcessInfoBox'
const axios = require('axios')
// import $ from 'jquery'
// Require needed datatables modules
// require('datatables.net')
// require('datatables.net-bs')
const stores = require('../../shared_state.js')

export default {
  name: 'Exchange',
  components: {
    Alert,
    InfoBox,
    ProcessInfoBox
  },
  watch: {
    account: function () {
      this.updateTransactions()
      this.updateBalance()
    }
  },
  data: function() {
    return {
      store: stores.store.state,
      exchangeAmountE2T: null,
      exchangeAmountT2E: null,
      balanceCent: 0,
      rateE2Tcent: 99,
      rateT2Ecent: 99,
      transactions: []
    }
  },
  computed: {
    account() {
      return this.store.account
    },
    exchangeAmountE2TConverted() {
      return (Math.floor(this.exchangeAmountE2T * this.rateE2Tcent) / 100).toFixed(2)
    },
    exchangeAmountT2EConverted() {
      return (Math.floor(this.exchangeAmountT2E * this.rateT2Ecent) / 100).toFixed(2)
    },
    rateE2T() {
      return (this.rateE2Tcent / 100).toFixed(2)
    },
    rateT2E() {
      return (this.rateT2Ecent / 100).toFixed(2)
    },
    balance() {
      return this.balanceCent / 100
    },
    isMobile () {
      return (window.innerWidth <= 800 && window.innerHeight <= 600)
    }
  },
  methods: {
    centToWhole (amount) {
      return (amount / 100).toFixed(2)
    },
    initExchangeE2T () {
      if (!this.exchangeAmountE2T) { return }
      let amount = this.exchangeAmountE2T * 100
      this.exchangeAmountE2T = null
      axios.post('/api/exchange/e2t', {
        collatoral_cent: amount,
        dest_wallet: this.account,
        counterparty: 'IBAN123'
      }).then(response => console.log(response.data.token))
      .then(this.updateTransactions())
    },
    initExchangeT2E () {
      if (!this.exchangeAmountT2E) { return }
      let amount = this.exchangeAmountT2E * 100
      this.exchangeAmountT2E = null
      axios.post('/api/exchange/t2e', {
        token_amount_cent: amount,
        destination_iban: 'IBAN123',
        counterparty: this.account
      }).then(response => console.log(response.data.token))
      .then(this.updateTransactions())
      this.store.account = 'hi'
    },
    confirmTransaction (paymentId, counterparty) {
      axios.post('/api/exchange/complete', {
        payment_id: paymentId,
        counterparty: counterparty
      }).then(response => console.log(response.data))
      axios.get('/api/exchange/payment', {
        params: {
          payment_id: paymentId
        }
      }).then(this.updateTransactions())
      .then(this.updateBalance())
    },
    updateBalance () {
      axios.get('/api/transactions/balance', {
        params: {
          wallet: this.account
        }
      }).then(response => { this.balanceCent = response.data.balance })
    },
    updateTransactions () {
      axios.get('/api/transactions/wallet', {
        params: {
          wallet: this.account
        }
      }).then(response => { this.transactions = response.data })
    },
    onlyForCurrencyE2T ($event) {
      // console.log($event.keyCode); //keyCodes value
      let keyCode = ($event.keyCode ? $event.keyCode : $event.which)

      // only allow number and one dot
      if ((keyCode < 48 || keyCode > 57) && (keyCode !== 46 || this.exchangeAmountE2T.indexOf('.') !== -1)) { // 46 is dot
        $event.preventDefault()
      }

      // restrict to 2 decimal places
      if (this.exchangeAmountE2T != null && this.exchangeAmountE2T.indexOf('.') > -1 && (this.exchangeAmountE2T.split('.')[1].length > 1)) {
        $event.preventDefault()
      }
    },
    onlyForCurrencyT2E ($event) {
      // console.log($event.keyCode); //keyCodes value
      let keyCode = ($event.keyCode ? $event.keyCode : $event.which)

      // only allow number and one dot
      if ((keyCode < 48 || keyCode > 57) && (keyCode !== 46 || this.exchangeAmountT2E.indexOf('.') !== -1)) { // 46 is dot
        $event.preventDefault()
      }

      // restrict to 2 decimal places
      if (this.exchangeAmountT2E != null && this.exchangeAmountT2E.indexOf('.') > -1 && (this.exchangeAmountT2E.split('.')[1].length > 1)) {
        $event.preventDefault()
      }
    }
  },
  mounted () {
    axios.get('/api/exchange/e2t/rate')
      .then(response => { this.rateE2Tcent = response.data.token })
    axios.get('/api/exchange/t2e/rate')
      .then(response => { this.rateT2Ecent = response.data.eur })
    this.updateBalance()
    this.updateTransactions()
    // this.$nextTick(() => {
    //   $('#example1').DataTable({
    //     'order': [],
    //     'oLanguage': {
    //       'sLengthMenu': 'Show _MENU_ transactions',
    //       'sInfo': 'Showing _START_ to _END_ of _TOTAL_ transactions'
    //     }
    //   })
    // })
  }
}
</script>
<style>
.info-box {
  cursor: pointer;
}
.info-box-content {
  text-align: center;
  vertical-align: middle;
  display: inherit;
}
.fullCanvas {
  width: 100%;
}
</style>
