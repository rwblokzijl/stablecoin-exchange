import moment from 'moment'

export const servers = [{
  name: 'Intrest rates',
  status: 'success',
  icon: 'globe',
  description: 'Loan configurations'
}, {
  name: 'Exchange rates',
  status: 'danger',
  icon: 'exchange',
  description: 'EuroToken vs Euro exchange rates'
}, {
  name: 'Bank settings',
  status: 'info',
  icon: 'home',
  description: 'Main DB server'
}, {
  name: 'Loan configurations',
  status: 'success',
  icon: 'file-code-o',
  description: 'Loan configurations'
}, {
  name: 'Identity management',
  status: 'success',
  icon: 'key',
  description: 'Configure keys and access'
}, {
  name: 'bkup01',
  status: 'warning',
  icon: 'backward',
  description: 'Backup server'
}]

export const stats = [{
  header: '8390',
  text: 'Visitors'
}, {
  header: '30%',
  text: 'Referrals'
}, {
  header: '70%',
  text: 'Organic'
}]

export const timeline = [{
  icon: 'fa-envelope',
  color: 'blue',
  title: 'Write short novel',
  time: moment().endOf('day').fromNow(),
  body: 'Etsy doostang zoodles disqus groupon greplin oooj voxy zoodles, weebly ning heekya handango imeem plugg dopplr jibjab, movity jajah plickers sifteo edmodo ifttt zimbra. Babblely odeo kaboodle quora plaxo ideeli hulu weebly balihoo...',
  buttons: [{
    type: 'primary',
    message: 'Read more',
    href: 'https://github.com/misterGF/CoPilot',
    target: '_blank'
  }]
},
{
  icon: 'fa-user',
  color: 'yellow',
  title: 'Sarah Young accepted your friend request',
  time: moment('20150620', 'MMM Do YY').fromNow()
},
{
  icon: 'fa-camera',
  color: 'purple',
  title: 'Watch a youTube video',
  time: moment('20130620', 'YYYYMMDD').fromNow(),
  body: '<div class="embed-responsive embed-responsive-16by9"><iframe width="560" height="315" src="https://www.youtube.com/embed/8aGhZQkoFbQ" frameborder="0" allowfullscreen></iframe></div>'
}]
