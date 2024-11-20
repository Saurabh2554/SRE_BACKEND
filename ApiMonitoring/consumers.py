# import json
# from channels.generic.websocket import WebsocketConsumer
# from channels.consumer import AsyncConsumer
# import asyncio
# import channels
# class MetricsConsumer(AsyncConsumer):
#     async def websocket_connect(self, event):
#         try:
#             print("inside the connect method")
#             # Access room_name and monitoringID from the URL path parameters
#             self.room_name = 'data' #self.scope['url_route']['kwargs']['room_name']
#             self.monitoringId = self.scope['url_route']['kwargs'].get('monitoringId', None)
            
#             # Create a unique group name based on room_name
#             self.room_group_name = f"metrics_{self.room_name}"

#             # Add this connection to the room group
#             await self.channel_layer.group_add(
#                 self.room_group_name,
#                 self.channel_name
#             )
            
#             await self.websocket_accept()

#             confirmation_message = {
#                 'type': 'connection_established',
#                 'message': 'Connection established successfully.'
#             }
#             await self.send(text_data=json.dumps(confirmation_message))
#         except Exception as e:
#           print(f"Exception occured as : {e}")    
        
#     async def websocket_disconnect(self, close_code):
#         try:
#             # Send a disconnect message before closing
#             print("inside disconnect")
#             disconnect_message = {
#                 'type': 'disconnection_notice',
#                 'message': 'You are about to be disconnected.'
#             }
#             await self.send(text_data=json.dumps(disconnect_message))

#             #  Leave room group
#             await self.channel_layer.group_discard(
#                 self.room_group_name,
#                 self.channel_name
#             )

#             # Close the connection
#             await self.close()
#         except channels.exceptions.StopConsumer as e:    
#             print(e)

#     async def websocket_receive(self):
#         try:
#             print("inside the receive")
#             pass
#         except:
#             pass 

#     async def send_metrics_update(self, event):
#         metrics = event['metrics']
#         await self.send(text_data=json.dumps({
#             'message': metrics
#         }))     

