---
name: pubsub
author: eightballer
version: 0.1.0
description: A protocol for Publish/Subscribe messaging systems, enabling message distribution through channel-based subscription and publishing.
license: Apache-2.0
aea_version: '>=1.0.0, <2.0.0'
protocol_specification_id: eightballer/pubsub:0.1.0
speech_acts:
  subscribe:
    channels: pt:list[pt:str]
  unsubscribe:
    channels: pt:list[pt:str]
  publish:
    channel: pt:str
    message: pt:bytes
  subscribed:
    channel: pt:str
    success: pt:bool
    info: pt:optional[pt:str]
  unsubscribed:
    channel: pt:str
    success: pt:bool
    info: pt:optional[pt:str]
  message:
    channel: pt:str
    data: pt:bytes
  error:
    data: pt:bytes
---
---
initiation: [subscribe, unsubscribe, publish]
reply:
  subscribe: [subscribed, error]
  unsubscribe: [unsubscribed, error]
  publish: [error]
  subscribed: []
  unsubscribed: []
  message: [message, error]
  error: []
termination: [subscribed, unsubscribed, error]
roles: {publisher, subscriber}
end_states: [subscribed, unsubscribed, error]
keep_terminal_state_dialogues: false