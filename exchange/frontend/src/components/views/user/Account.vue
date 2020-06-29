<template>
  <!-- Main content -->
  <section class="content">
    <!-- GitHub hint -->
    <div class="row justify-content-center">

      <!-- Info boxes -->
      <div class="col-md-3 col-sm-6 col-xs-12">
        <info-box color-class="bg-green"
                  :icon-classes="['fa', 'fa-arrow-down']"
                  text="Received this month"
                  number="230.57"></info-box>
      </div>
      <!-- /.col -->
      <div class="col-md-3 col-sm-6 col-xs-12">
        <info-box color-class="bg-red"
                  :icon-classes="['fa', 'fa-arrow-up']"
                  text="Sent this month"
                  number="41,410"></info-box>
      </div>
      <!-- /.col -->
    </div>
    <div class="row justify-content-center">
      <!-- fix for small devices only -->
      <div class="clearfix visible-sm-block"></div>

      <!-- /.col -->
      <div class="col-md-3 col-sm-6 col-xs-12">
        <info-box color-class="bg-yellow"
                  :icon-classes="['fa', 'fa-eur']"
                  text="Current Balance"
                  number="2,000"></info-box>
      </div>
      <!-- /.col -->
    </div>
    <!-- /.row -->

    <div class="row">
      <div class="col-xs-12">
        <h2>Transfer</h2>
      </div>
      <!-- with characthers -->
      <div class="col-md-3 col-sm-6 col-xs-12">
        <div class="input-group">
          <span class="input-group-addon">
            <i class="fa fa-fw fa-at" aria-hidden="true"></i>
          </span>
          <input class="form-control" placeholder="Counterparty" type="text">
        </div>
      </div>
      <div class="col-md-3 col-sm-6 col-xs-12">
        <div class="input-group">
        <span class="input-group-addon">
          <i class="fa fa-fw fa-eur" aria-hidden="true"></i>
        </span>
        <input class="form-control" type="text">
        <span class="input-group-addon">.00</span>
      </div>
      </div>
    </div>

    <div class="row">
      <div class="col-xs-12">
        <h2>Transaction History</h2>
      </div>
      <div class="col-md-6 col-xs-12">
        <table
          role="grid"
          id="example1"
          class="table table-bordered table-striped dataTable">
          <thead>
            <tr role="row">
              <th style="width: 167px;" colspan="1" rowspan="1" tabindex="0">
                Date
              </th>
              <th style="width: 207px;" colspan="1" rowspan="1" tabindex="0" >
                Counterparty
              </th>
                <th style="width: 182px;" colspan="1" rowspan="1" tabindex="0" >
                  Amount
                </th>
                  <th style="width: 142px;" colspan="1" rowspan="1" tabindex="0" >
                    In/Out
                  </th>
                    <th style="width: 101px;" colspan="1" rowspan="1" tabindex="0" >
                      Description
                    </th>
                      <th style="width: 101px;" colspan="1" rowspan="1" tabindex="0" >
                        Status
                      </th>
            </tr>
          </thead>
          <tbody>
            <tr class="even" role="row">
              <td>2020 May 28 22:19</td>
              <td>Alice</td>
              <td>6.00 €T</td>
              <td>In</td>
              <td>Drinks</td>
              <td>Pending</td>
            </tr>
            <tr class="odd" role="row">
              <td>2020 May 28 17:48</td>
              <td>Albert Heijn</td>
              <td>22.45 €T</td>
              <td>Out</td>
              <td>Id: 395729</td>
              <td>Confirmed</td>
            </tr>
            <tr class="even" role="row">
              <td>2020 May 28 11:34</td>
              <td>Lunchbar</td>
              <td>7.29 €T</td>
              <td>Out</td>
              <td></td>
              <td>Confirmed</td>
            </tr>
            <tr class="odd" role="row">
              <td>2020 May 28 8:23</td>
              <td>Coffee Machine</td>
              <td>0.99 €T</td>
              <td>Out</td>
              <td></td>
              <td>Confirmed</td>
            </tr>
            <tr class="even" role="row">
              <td>2020 May 27 22:19</td>
              <td>Alice</td>
              <td>6.00 €T</td>
              <td>In</td>
              <td>Drinks</td>
              <td>Confirmed</td>
            </tr>
            <tr class="odd" role="row">
              <td>2020 May 27 17:48</td>
              <td>Albert Heijn</td>
              <td>22.45 €T</td>
              <td>Out</td>
              <td>Id: 857395</td>
              <td>Confirmed</td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <th colspan="1" rowspan="1">Date</th>
              <th colspan="1" rowspan="1">Counterparty</th>
              <th colspan="1" rowspan="1">Amount</th>
              <th colspan="1" rowspan="1">In/Out</th>
              <th colspan="1" rowspan="1">Description</th>
              <th colspan="1" rowspan="1">Status</th>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>

    <!-- Main row -->
    <div class="row">
      <div class="col-md-3 col-sm-6 col-xs-12">
        <process-info-box color-class="bg-green"
                          :icon-classes="['fa', 'fa-arrow-up']"
                          text="Received this month"
                          number="2030.57"
                          :progress="50"
                          description="50% increase since May"></process-info-box>
      </div>
      <!-- /.col -->
      <div class="col-md-3 col-sm-6 col-xs-12">
        <process-info-box color-class="bg-red"
                          :icon-classes="['fa', 'fa-arrow-down']"
                          text="Sent this month"
                          number="329.57"
                          :progress="20"
                          description="20% increase in 30 days"></process-info-box>
      </div>
      <!-- /.col -->
    </div>
    <!-- /.row -->
  </section>
  <!-- /.content -->
</template>

<script>
import Chart from 'chart.js'
import Alert from '../../widgets/Alert'
import InfoBox from '../../widgets/InfoBox'
import ProcessInfoBox from '../../widgets/ProcessInfoBox'

export default {
  name: 'Wallet',
  components: {
    Alert,
    InfoBox,
    ProcessInfoBox
  },
  data () {
    return {
      generateRandomNumbers (numbers, max, min) {
        var a = []
        for (var i = 0; i < numbers; i++) {
          a.push(Math.floor(Math.random() * (max - min + 1)) + max)
        }
        return a
      }
    }
  },
  computed: {
    coPilotNumbers () {
      return this.generateRandomNumbers(12, 1000000, 10000)
    },
    personalNumbers () {
      return this.generateRandomNumbers(12, 1000000, 10000)
    },
    isMobile () {
      return (window.innerWidth <= 800 && window.innerHeight <= 600)
    }
  },
  mounted () {
    this.$nextTick(() => {
      var ctx = document.getElementById('trafficBar').getContext('2d')
      var config = {
        type: 'line',
        data: {
          labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
          datasets: [{
            label: 'CoPilot',
            fill: false,
            borderColor: '#284184',
            pointBackgroundColor: '#284184',
            backgroundColor: 'rgba(0, 0, 0, 0)',
            data: this.coPilotNumbers
          }, {
            label: 'Personal Site',
            borderColor: '#4BC0C0',
            pointBackgroundColor: '#4BC0C0',
            backgroundColor: 'rgba(0, 0, 0, 0)',
            data: this.personalNumbers
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: !this.isMobile,
          legend: {
            position: 'bottom',
            display: true
          },
          tooltips: {
            mode: 'label',
            xPadding: 10,
            yPadding: 10,
            bodySpacing: 10
          }
        }
      }

      new Chart(ctx, config) // eslint-disable-line no-new

      var pieChartCanvas = document.getElementById('languagePie').getContext('2d')
      var pieConfig = {
        type: 'pie',
        data: {
          labels: ['HTML', 'JavaScript', 'CSS'],
          datasets: [{
            data: [56.6, 37.7, 4.1],
            backgroundColor: ['#00a65a', '#f39c12', '#00c0ef'],
            hoverBackgroundColor: ['#00a65a', '#f39c12', '#00c0ef']
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: !this.isMobile,
          legend: {
            position: 'bottom',
            display: true
          }
        }
      }

      new Chart(pieChartCanvas, pieConfig) // eslint-disable-line no-new
    })
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
