# Generated migration to add community models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_add_missing_fields'),
    ]

    operations = [
        # Create Community model
        migrations.CreateModel(
            name='Community',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=100, null=True, unique=True)),
                ('description', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='communities/')),
                ('cover_image', models.ImageField(blank=True, null=True, upload_to='communities/covers/')),
                ('member_count', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_communities', to='auth.user')),
            ],
            options={
                'verbose_name_plural': 'Communities',
                'ordering': ['-created_at'],
            },
        ),
        # Create CommunityMember model
        migrations.CreateModel(
            name='CommunityMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('admin', 'Admin'), ('moderator', 'Moderator'), ('member', 'Member')], default='member', max_length=20)),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='core.community')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='community_members', to='auth.user')),
            ],
            options={
                'verbose_name_plural': 'Community Members',
            },
        ),
        # Create CommunityPost model
        migrations.CreateModel(
            name='CommunityPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('post_type', models.CharField(choices=[('post', 'Post'), ('announcement', 'Announcement'), ('question', 'Question')], default='post', max_length=20)),
                ('image', models.ImageField(blank=True, null=True, upload_to='community_posts/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='community_posts', to='auth.user')),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='core.community')),
            ],
            options={
                'verbose_name_plural': 'Community Posts',
                'ordering': ['-created_at'],
            },
        ),
        # Create CommunityComment model
        migrations.CreateModel(
            name='CommunityComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='community_comments', to='auth.user')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='core.communitypost')),
            ],
            options={
                'verbose_name_plural': 'Community Comments',
                'ordering': ['created_at'],
            },
        ),
        # Create CommunityLike model
        migrations.CreateModel(
            name='CommunityLike',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='core.communitypost')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='community_likes', to='auth.user')),
            ],
            options={
                'verbose_name_plural': 'Community Likes',
            },
        ),
    ]
