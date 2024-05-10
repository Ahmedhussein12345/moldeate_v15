        session.on('bye', function() {
                console.log('Event: Bye');
                setTimeout(function () {
                    console.log("((((((((((((((((((((((((((((((((((((((((((((((")
                    self.platform.get('/restapi/v1.0/account/~/extension/~/call-log-sync?statusGroup=All&syncType=FSync&recordCount=1').then(function(results) {

                        var record = results.json()
                        console.log("var record", record)
                        var rec_li = [];
                        _.each(record['records'], function(result) {
                            if (result && result.from && (result.from.phoneNumber == to_number && result.result == 'Accepted' || result.to.phoneNumber == to_number && result.result == 'Call connected')) {
                                var url = self.ringcentral_service_uri.split("/login/");
                                var time = new Date().getTime()
                                var rec_type = ''
                                var str = ''
                                var data_li = []
                                var duration = result.duration / 60
                                if (result.legs) {
                                    _.each(result.legs, function(leg) {
                                        var val = {
                                            'name': leg.action,
                                            'call_type': leg.direction,
                                            'leg_type': leg.legType,
                                            'from_number': leg.from.phoneNumber,
                                            'to_number': leg.to.phoneNumber
                                        }
                                        data_li.push([0, 0, val])
                                    })
                                }
                                if (result.recording) {
                                    console.log(":::::::::33333333333");

                                    if (result.recording.type == 'Automatic') {
                                        rec_type = 'Auto'
                                    } else {
                                        rec_type = result.recording.type
                                    }

                                    var str = url[0] + '/mobile/media?cmd=downloadMessage&msgid=' + result.recording.id + '&useName=true&time=' + '1554700788480' + '&msgExt=&msgNum=' + result.from.phoneNumber + '&msgDir=' + result.direction + '&msgRecType=' + rec_type + '&msgRecId=' + result.recording.id + '&type=1&download=1&saveMsg=&file=.mp3'
                                    rpc.query({
                                        model: 'crm.phonecall',
                                        method: 'create_search_voip',
                                        args: [{
                                            'name': from_number,
                                            'type': type,
                                            'partner_phone': to_number,
                                            'date': moment.utc(result.startTime),
                                            'description': $modal_outgoing_call.find('#description').val(),
                                            'duration': duration,
                                            'crm_phonecall_about_id': $modal_outgoing_call.find('select[name="phonecall_about"]').val(),
                                            'ringcentral_call_id': result.id,
                                            'ringcentral_call_url': str,
                                            'is_recording': true,
                                            'crm_call_activity_ids': data_li
                                        }],
                                    })
                                } else {
                                    console.log(":::::::::4444444444");

                                    rpc.query({
                                        model: 'crm.phonecall',
                                        method: 'create_search_voip',
                                        args: [{
                                            'name': from_number,
                                            'type': type,
                                            'partner_phone': to_number,
                                            'date': moment.utc(result.startTime),
                                            'description': $modal_outgoing_call.find('#description').val(),
                                            'duration': duration,
                                            'crm_phonecall_about_id': $modal_outgoing_call.find('select[name="phonecall_about"]').val(),
                                            'ringcentral_call_id': result.id,
                                            'crm_call_activity_ids': data_li
                                        }],
                                    })
                                }
                            }
                        })
                    })
                    
                }, 3000);
                close();
            });