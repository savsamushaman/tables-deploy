import json

from business.models import BusinessModel
from tray.models import OrderModel, OrderItem

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver


class FeedConsumer(WebsocketConsumer):
    def connect(self):
        feed_slug = self.scope['url_route']['kwargs']['biz_slug']
        self.feed_group_name = 'feed_%s' % feed_slug
        user = self.scope['user']
        try:
            business = BusinessModel.objects.get(slug=feed_slug)
            if business.is_active:
                if user in business.admins.all() or user in business.staff.all():
                    # Join room group
                    async_to_sync(self.channel_layer.group_add)(self.feed_group_name, self.channel_name)
                    self.accept()
        except BusinessModel.DoesNotExist:
            pass

    def disconnect(self, code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.feed_group_name,
            self.channel_name,
        )

    # Receive message from WebSocket
    def receive(self, text_data):

        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        event = text_data_json['event']
        user = self.scope['user']

        # HANDLE ORDER
        if event == 'handle_order':
            try:
                order = OrderModel.objects.get(id=message)
                if order.status == 'PL' and order.handler is None:
                    order.handler = user
                    order.status = 'S'
                    order.save()

                    self.send(text_data=json.dumps({
                        'message': message,
                        'event': 'handle_order_success',
                    }))

                    # Send message to room group
                    async_to_sync(self.channel_layer.group_send)(
                        self.feed_group_name,
                        {
                            'type': 'feed_update',
                            'message': message,
                            'event': 'handle_order_by_someone',
                            'user': user.username
                        }
                    )

                else:

                    self.send(text_data=json.dumps({
                        'message': message,
                        'event': 'handle_order_fail_not_allowed',

                    }))

            except OrderModel.DoesNotExist:
                self.send(text_data=json.dumps({
                    'message': message,
                    'event': 'handle_order_fail_non_existent',
                }))

        # CANCEL ORDER
        if event == 'cancel_order':
            try:
                order = OrderModel.objects.get(id=message)
                if order.status == 'S' and order.handler.username == user.username:
                    order.status = 'C'
                    order.save()
                else:
                    self.send(text_data=json.dumps({
                        'message': message,
                        'event': 'cancel_order_fail_not_allowed',
                    }))

            except OrderModel.DoesNotExist:
                self.send(text_data=json.dumps({
                    'message': message,
                    'event': 'cancel_order_fail_non_existent',

                }))

        # MARK ORDER AS DONE
        if event == 'mark_as_done':
            try:
                order = OrderModel.objects.get(id=message)
                if order.status == 'S' and order.handler.username == user.username:
                    order.status = 'P'
                    order.save()

                    async_to_sync(self.channel_layer.group_send)(
                        self.feed_group_name,
                        {
                            'type': 'feed_update',
                            'message': message,
                            'event': 'mark_as_done_success',
                        }
                    )

                else:

                    self.send(text_data=json.dumps({
                        'message': message,
                        'event': 'mark_as_done_fail_not_allowed',
                    }))

            except OrderModel.DoesNotExist:
                self.send(text_data=json.dumps({
                    'message': message,
                    'event': 'mark_as_done_fail_non_existent',
                }))

    # Receive message from room group
    def feed_update(self, event):
        message = event['message']
        curr_event = event['event']
        user = event.get('user', None)

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'event': curr_event,
            'user': user

        }))


@receiver(post_save, sender=OrderModel)
def update_order_feed(sender, instance, created, **kwargs):
    if created:
        pass
    else:
        if instance.new:
            event = 'new_order'
            instance.set_new_to_false()
            item_dict = dict()
            items = OrderItem.objects.filter(order=instance)

            for item in items:
                item_dict[item.product.name] = item.quantity

            order_dict = {
                'customer': instance.customer.username,
                'customer_first_name': instance.customer.first_name,
                'customer_last_name': instance.customer.last_name,
                'table': instance.table.table_nr,
                'pk': instance.pk,
                'status': instance.status,
                'total': instance.return_total(),
                'items': item_dict,
            }

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'feed_{instance.business.slug}', {
                    'type': 'feed_update',
                    'message': order_dict,
                    'event': event
                }
            )

        elif instance.status == 'C':
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'feed_{instance.business.slug}',
                {
                    'type': 'feed_update',
                    'message': instance.pk,
                    'event': 'cancel_order_by_someone',
                }
            )
