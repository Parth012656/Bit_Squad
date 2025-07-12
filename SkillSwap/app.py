from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from functools import wraps



# Import extensions
from extensions import db, login_manager

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'static/images/profile_photos'

# Helper for allowed file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://skillswap_user:root@localhost/skillswap_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    # Load configuration
    
    # Add upload folder configuration
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    # Import models after db is initialized
    from models.user import User
    from models.skill import Skill
    from models.exchange import Exchange
    from models.admin import PlatformMessage, ModerationAction, Report
    from models.notification import Notification
    from models.chat import ChatRoom, ChatMessage
    from models.availability import Availability, ExchangeSchedule
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Admin decorator
    def admin_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.is_admin():
                flash('Access denied. Admin privileges required.')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    
    # Admin dashboard
    @app.route('/admin')
    @login_required
    @admin_required
    def admin_dashboard():
        """Admin dashboard"""
        total_users = User.query.count()
        total_skills = Skill.query.count()
        total_exchanges = Exchange.query.count()
        pending_reports = Report.query.filter_by(status='pending').count()
        banned_users = User.query.filter_by(is_banned=True).count()
        
        recent_exchanges = Exchange.query.order_by(Exchange.created_at.desc()).limit(10).all()
        recent_reports = Report.query.order_by(Report.created_at.desc()).limit(5).all()
        
        return render_template('admin/dashboard.html', 
                            total_users=total_users,
                            total_skills=total_skills,
                            total_exchanges=total_exchanges,
                            pending_reports=pending_reports,
                            banned_users=banned_users,
                            recent_exchanges=recent_exchanges,
                            recent_reports=recent_reports)
    
    # User management
    @app.route('/admin/users')
    @login_required
    @admin_required
    def admin_users():
        """User management page"""
        page = request.args.get('page', 1, type=int)
        per_page = 20
        users = User.query.paginate(page=page, per_page=per_page, error_out=False)
        return render_template('admin/users.html', users=users)
    
    @app.route('/admin/user/<int:user_id>/ban', methods=['POST'])
    @login_required
    @admin_required
    def ban_user(user_id):
        """Ban a user"""
        user = User.query.get_or_404(user_id)
        reason = request.form.get('reason', 'No reason provided')
        
        if user.id == current_user.id:
            flash('You cannot ban yourself!')
            return redirect(url_for('admin_users'))
        
        user.ban_user(reason, current_user)
        db.session.commit()
        
        # Log moderation action
        action = ModerationAction(
            action_type='user_banned',
            target_type='user',
            target_id=user.id,
            reason=reason,
            moderator_id=current_user.id
        )
        db.session.add(action)
        db.session.commit()
        
        flash(f'User {user.name} has been banned.')
        return redirect(url_for('admin_users'))
    
    @app.route('/admin/user/<int:user_id>/unban', methods=['POST'])
    @login_required
    @admin_required
    def unban_user(user_id):
        """Unban a user"""
        user = User.query.get_or_404(user_id)
        user.unban_user()
        db.session.commit()
        
        # Log moderation action
        action = ModerationAction(
            action_type='user_unbanned',
            target_type='user',
            target_id=user.id,
            reason='User unbanned',
            moderator_id=current_user.id
        )
        db.session.add(action)
        db.session.commit()
        
        flash(f'User {user.name} has been unbanned.')
        return redirect(url_for('admin_users'))
    
    # Content moderation
    @app.route('/admin/skills')
    @login_required
    @admin_required
    def admin_skills():
        """Skill moderation page"""
        page = request.args.get('page', 1, type=int)
        per_page = 20
        skills = Skill.query.paginate(page=page, per_page=per_page, error_out=False)
        return render_template('admin/skills.html', skills=skills)
    
    @app.route('/admin/skill/<int:skill_id>/reject', methods=['POST'])
    @login_required
    @admin_required
    def reject_skill(skill_id):
        """Reject a skill"""
        skill = Skill.query.get_or_404(skill_id)
        reason = request.form.get('reason', 'Inappropriate content')
        
        # Log moderation action
        action = ModerationAction(
            action_type='skill_rejected',
            target_type='skill',
            target_id=skill.id,
            reason=reason,
            moderator_id=current_user.id
        )
        db.session.add(action)
        
        # Remove the skill
        db.session.delete(skill)
        db.session.commit()
        
        flash(f'Skill "{skill.name}" has been rejected and removed.')
        return redirect(url_for('admin_skills'))
    
    # Reports management
    @app.route('/admin/reports')
    @login_required
    @admin_required
    def admin_reports():
        """Reports management page"""
        page = request.args.get('page', 1, type=int)
        per_page = 20
        reports = Report.query.order_by(Report.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return render_template('admin/reports.html', reports=reports)
    
    @app.route('/admin/report/<int:report_id>/resolve', methods=['POST'])
    @login_required
    @admin_required
    def resolve_report(report_id):
        """Resolve a report"""
        report = Report.query.get_or_404(report_id)
        action = request.form.get('action')  # 'dismiss', 'ban_user', 'remove_content'
        reason = request.form.get('reason', 'Report resolved')
        
        report.status = 'resolved'
        report.resolved_at = datetime.utcnow()
        report.resolved_by = current_user.id
        db.session.commit()
        
        flash(f'Report #{report.id} has been resolved.')
        return redirect(url_for('admin_reports'))
    
    # Platform messaging
    @app.route('/admin/messages')
    @login_required
    @admin_required
    def admin_messages():
        """Platform messages management"""
        messages = PlatformMessage.query.order_by(PlatformMessage.created_at.desc()).all()
        return render_template('admin/messages.html', messages=messages)
    
    @app.route('/admin/messages/create', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def create_message():
        """Create a platform message"""
        if request.method == 'POST':
            title = request.form.get('title')
            message = request.form.get('message')
            message_type = request.form.get('message_type', 'info')
            
            platform_message = PlatformMessage(
                title=title,
                message=message,
                message_type=message_type,
                created_by=current_user.id
            )
            db.session.add(platform_message)
            db.session.commit()
            
            # Notify all users about the new platform message
            all_users = User.query.filter_by(is_banned=False).all()
            for user in all_users:
                create_notification(
                    user_id=user.id,
                    title=f"Platform Update: {title}",
                    message=f"New platform message: {message[:100]}{'...' if len(message) > 100 else ''}",
                    notification_type='platform_message',
                    related_id=platform_message.id,
                    related_type='platform_message'
                )
            
            flash('Platform message created and sent to all users!')
            return redirect(url_for('admin_messages'))
        
        return render_template('admin/create_message.html')
    
    @app.route('/admin/messages/<int:message_id>/toggle', methods=['POST'])
    @login_required
    @admin_required
    def toggle_message(message_id):
        """Toggle message active status"""
        message = PlatformMessage.query.get_or_404(message_id)
        message.is_active = not message.is_active
        db.session.commit()
        
        status = 'activated' if message.is_active else 'deactivated'
        flash(f'Message "{message.title}" has been {status}.')
        return redirect(url_for('admin_messages'))
    
    # Reports and analytics
    @app.route('/admin/reports/download')
    @login_required
    @admin_required
    def download_reports():
        """Download comprehensive reports with user activity"""
        from io import StringIO
        import csv
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Report Type', 'User Activity', 'Feedback', 'Swap Activity', 'Date', 'Reporter', 'Status'])
        
        # Get all reports
        reports = Report.query.all()
        for report in reports:
            user = User.query.get(report.reporter_id)
            user_activity = f"User: {user.name if user else 'Unknown'}, Rating: {user.total_rating if user else 0}"
            
            # Get user's feedback count
            feedback_count = Exchange.query.filter_by(
                offering_user_id=user.id if user else 0
            ).filter(Exchange.feedback.isnot(None)).count()
            
            # Get user's swap activity
            swap_count = Exchange.query.filter_by(
                offering_user_id=user.id if user else 0, status='Completed'
            ).count()
            
            writer.writerow([
                report.report_type,
                user_activity,
                f"{feedback_count} feedbacks",
                f"{swap_count} swaps",
                report.created_at.strftime('%Y-%m-%d %H:%M') if report.created_at else 'Unknown',
                user.name if user else 'Unknown',
                report.status
            ])
        
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=user_activity_report.csv'}
        )
    
    @app.route('/admin/analytics')
    @login_required
    @admin_required
    def admin_analytics():
        """Analytics dashboard"""
        # User statistics
        total_users = User.query.count()
        new_users_this_month = User.query.filter(
            User.created_at >= datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        ).count()
        
        # Exchange statistics
        total_exchanges = Exchange.query.count()
        completed_exchanges = Exchange.query.filter_by(status='Completed').count()
        pending_exchanges = Exchange.query.filter_by(status='Pending').count()
        
        # Skill statistics
        total_skills = Skill.query.count()
        skills_by_category = db.session.query(Skill.category, db.func.count(Skill.id)).group_by(Skill.category).all()
        
        # Moderation statistics
        banned_users = User.query.filter_by(is_banned=True).count()
        pending_reports = Report.query.filter_by(status='pending').count()
        
        return render_template('admin/analytics.html',
                            total_users=total_users,
                            new_users_this_month=new_users_this_month,
                            total_exchanges=total_exchanges,
                            completed_exchanges=completed_exchanges,
                            pending_exchanges=pending_exchanges,
                            total_skills=total_skills,
                            skills_by_category=skills_by_category,
                            banned_users=banned_users,
                            pending_reports=pending_reports)
    
    @app.route('/admin/analytics/download')
    @login_required
    @admin_required
    def download_analytics():
        """Download comprehensive analytics report"""
        from io import StringIO
        import csv
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Metric', 'Value', 'Description'])
        
        # Get analytics data
        total_users = User.query.count()
        new_users_this_month = User.query.filter(
            User.created_at >= datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        ).count()
        total_exchanges = Exchange.query.count()
        completed_exchanges = Exchange.query.filter_by(status='Completed').count()
        pending_exchanges = Exchange.query.filter_by(status='Pending').count()
        total_skills = Skill.query.count()
        banned_users = User.query.filter_by(is_banned=True).count()
        pending_reports = Report.query.filter_by(status='pending').count()
        
        # Write data
        writer.writerow(['Total Users', total_users, 'Total registered users'])
        writer.writerow(['New Users This Month', new_users_this_month, 'Users registered this month'])
        writer.writerow(['Total Skills', total_skills, 'Total skills shared'])
        writer.writerow(['Total Exchanges', total_exchanges, 'Total exchanges initiated'])
        writer.writerow(['Completed Exchanges', completed_exchanges, 'Successfully completed exchanges'])
        writer.writerow(['Pending Exchanges', pending_exchanges, 'Exchanges awaiting completion'])
        writer.writerow(['Banned Users', banned_users, 'Users currently banned'])
        writer.writerow(['Pending Reports', pending_reports, 'Reports awaiting review'])
        
        # Add completion rate
        completion_rate = (completed_exchanges / total_exchanges * 100) if total_exchanges > 0 else 0
        writer.writerow(['Completion Rate', f"{completion_rate:.1f}%", 'Percentage of completed exchanges'])
        
        # Add skills by category
        writer.writerow([])  # Empty row
        writer.writerow(['Skills by Category', '', ''])
        skills_by_category = db.session.query(Skill.category, db.func.count(Skill.id)).group_by(Skill.category).all()
        for category, count in skills_by_category:
            percentage = (count / total_skills * 100) if total_skills > 0 else 0
            writer.writerow([category, count, f"{percentage:.1f}% of total skills"])
        
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=skillify_analytics_report.csv'}
        )
    
    @app.route('/admin/update-badges', methods=['POST'])
    @login_required
    @admin_required
    def update_all_badges():
<<<<<<< HEAD
        """Update badges for all users based on current ratings and activity"""
        try:
            User.update_all_badges()
            flash('All user badges have been updated successfully!')
=======
        """Update badges for all users based on current ratings only"""
        try:
            User.update_all_badges()
            flash('All user badges have been updated based on ratings!')
>>>>>>> 60c18a0359b7bf6ae677c56f69f1ddc24a93ee99
        except Exception as e:
            flash(f'Error updating badges: {str(e)}')
        return redirect(url_for('admin_dashboard'))
    
    @app.route('/admin/send-notification', methods=['POST'])
    @login_required
    @admin_required
    def send_platform_notification():
        """Send immediate platform-wide notification"""
        title = request.form.get('title')
        message = request.form.get('message')
        notification_type = request.form.get('notification_type', 'info')
        
        if not title or not message:
            flash('Title and message are required!')
            return redirect(url_for('admin_dashboard'))
        
        # Send notification to all active users
        all_users = User.query.filter_by(is_banned=False).all()
        notification_count = 0
        
        for user in all_users:
            create_notification(
                user_id=user.id,
                title=title,
                message=message,
                notification_type=notification_type
            )
            notification_count += 1
        
        flash(f'Platform notification sent to {notification_count} users!')
        return redirect(url_for('admin_dashboard'))
    
    # Profile photo upload
    @app.route('/upload_photo', methods=['POST'])
    @login_required
    def upload_photo():
        if 'photo' not in request.files:
            flash('No file part')
            return redirect(url_for('dashboard'))
        file = request.files['photo']
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('dashboard'))
        if file and allowed_file(file.filename):
            filename = secure_filename(f"user_{current_user.id}_" + file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            current_user.profile_photo = filename
            db.session.commit()
            flash('Profile photo updated!')
        else:
            flash('Invalid file type')
        return redirect(url_for('dashboard'))

    # Profile visibility toggle
    @app.route('/toggle_visibility', methods=['POST'])
    @login_required
    def toggle_visibility():
        current_user.is_public = not current_user.is_public
        db.session.commit()
        flash(f"Profile visibility set to {'Public' if current_user.is_public else 'Private'}.")
        return redirect(url_for('dashboard'))

    # Skills list with pagination
    @app.route('/skills')
    def skills():
        page = request.args.get('page', 1, type=int)
        category = request.args.get('category', '')
        level = request.args.get('level', '')
        search = request.args.get('search', '')
        per_page = 6
        
        # Build query with filters
        skills_query = Skill.query.join(User).filter(User.is_public == True)
        
        if category:
            skills_query = skills_query.filter(Skill.category == category)
        if level:
            skills_query = skills_query.filter(Skill.level == level)
        if search:
            skills_query = skills_query.filter(
                db.or_(
                    Skill.name.contains(search),
                    Skill.description.contains(search),
                    User.name.contains(search)
                )
            )
        
        skills_paginated = skills_query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Add user profile photo, badge, and rating to each skill
        for skill in skills_paginated.items:
            skill.user_profile_photo = skill.user.profile_photo if skill.user else None
            skill.user_name = skill.user.name if skill.user else 'Unknown'
            skill.user_badge = skill.user.badge if skill.user else None
            skill.user_rating = skill.user.total_rating if skill.user else 0
            skill.user_skills_count = Skill.query.filter_by(user_id=skill.user.id).count() if skill.user else 0
            skill.user_required_skills_count = Exchange.query.filter_by(requesting_user_id=skill.user.id, status='Completed').count() if skill.user else 0
        
        return render_template('skills.html', 
                            skills=skills_paginated.items, 
                            pagination=skills_paginated,
                            current_category=category,
                            current_level=level,
                            current_search=search)

    # Swap request management (accept/reject/complete/cancel)
    @app.route('/exchange/<int:exchange_id>/action', methods=['POST'])
    @login_required
    def exchange_action(exchange_id):
        action = request.form.get('action')
        exchange = Exchange.query.get_or_404(exchange_id)
        
        # Validate that the exchange has valid skill references
        if not exchange.offered_skill_id or not exchange.requested_skill_id:
            flash('Invalid exchange data. Please contact support.')
            return redirect(url_for('dashboard'))
        
        if action == 'accept' and exchange.status == 'Pending' and exchange.requesting_user_id == current_user.id:
            exchange.status = 'Accepted'
            exchange.update_timestamp()
        elif action == 'reject' and exchange.status == 'Pending' and exchange.requesting_user_id == current_user.id:
            exchange.status = 'Rejected'
            exchange.update_timestamp()
        elif action == 'cancel' and exchange.status == 'Pending' and exchange.offering_user_id == current_user.id:
            exchange.status = 'Cancelled'
            exchange.update_timestamp()
        elif action == 'complete' and exchange.status == 'Accepted' and (exchange.offering_user_id == current_user.id or exchange.requesting_user_id == current_user.id):
            exchange.status = 'Completed'
            exchange.completed_at = datetime.utcnow()
            exchange.update_timestamp()
        else:
            flash('Invalid action or insufficient permissions.')
            return redirect(url_for('dashboard'))
        
        try:
            db.session.commit()
            flash(f'Exchange {action}ed successfully!')
        except Exception as e:
            db.session.rollback()
            flash('Error updating exchange. Please try again.')
            print(f"Exchange update error: {e}")
        
        return redirect(url_for('dashboard'))


    
    # Routes
    @app.route('/')
    def index():
        """Home page route"""
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login route"""
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            user = User.query.filter_by(email=email).first()
            
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                # Redirect admins to admin panel
                if user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password')
        
        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """Registration route"""
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered')
                return render_template('register.html')
            
            user = User(name=name, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        
        return render_template('register.html')

    @app.route('/dashboard')
    @login_required
    def dashboard():
        """User dashboard"""
        skills = Skill.query.filter_by(user_id=current_user.id).all()
        
        # Get user's exchanges (both offered and received)
        offered_exchanges = Exchange.query.filter_by(offering_user_id=current_user.id).all()
        received_exchanges = Exchange.query.filter_by(requesting_user_id=current_user.id).all()
        
        return render_template('dashboard.html', 
                            skills=skills,
                            offered_exchanges=offered_exchanges,
                            received_exchanges=received_exchanges)

    @app.route('/exchange/<int:skill_id>')
    @login_required
    def exchange(skill_id):
        """Skill exchange page"""
        skill = Skill.query.get_or_404(skill_id)
        # Add user profile photo to skill
        skill.user_profile_photo = skill.user.profile_photo if skill.user else None
        return render_template('exchange.html', skill=skill)

    @app.route('/logout')
    @login_required
    def logout():
        """Logout route"""
        logout_user()
        return redirect(url_for('index'))

    # API Routes
    @app.route('/api/skills', methods=['GET'])
    def api_skills():
        """API endpoint to get all skills"""
        skills = Skill.query.all()
        return jsonify([skill.to_dict() for skill in skills])

    @app.route('/api/skills', methods=['POST'])
    @login_required
    def api_create_skill():
        """API endpoint to create a new skill"""
        data = request.get_json()
        skill = Skill(
            name=data['name'],
            description=data['description'],
            category=data['category'],
            level=data['level'],
            user_id=current_user.id
        )
        db.session.add(skill)
        db.session.commit()
        return jsonify(skill.to_dict()), 201
    
    @app.route('/api/skills/<int:skill_id>', methods=['PUT'])
    @login_required
    def api_update_skill(skill_id):
        """API endpoint to update a skill"""
        skill = Skill.query.get_or_404(skill_id)
        
        # Check if user owns this skill
        if skill.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        skill.name = data['name']
        skill.description = data['description']
        skill.category = data['category']
        skill.level = data['level']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Skill updated successfully'
        })
    
    @app.route('/delete_skill/<int:skill_id>', methods=['POST'])
    @login_required
    def delete_skill(skill_id):
        """Delete a skill"""
        skill = Skill.query.get_or_404(skill_id)
        
        # Check if user owns this skill
        if skill.user_id != current_user.id:
            flash('You can only delete your own skills!')
            return redirect(url_for('dashboard'))
        
        db.session.delete(skill)
        db.session.commit()
        
        flash('Skill deleted successfully!')
        return redirect(url_for('dashboard'))
    

    
    # User reporting functionality
    @app.route('/report/<string:target_type>/<int:target_id>', methods=['GET', 'POST'])
    @login_required
    def report_content(target_type, target_id):
        """Report inappropriate content"""
        if request.method == 'POST':
            report_type = request.form.get('report_type')
            description = request.form.get('description')
            
            report = Report(
                report_type=report_type,
                target_type=target_type,
                target_id=target_id,
                description=description,
                reporter_id=current_user.id
            )
            db.session.add(report)
            db.session.commit()
            
            # Create notification for all admins
            admins = User.query.filter_by(role='admin').all()
            for admin in admins:
                create_notification(
                    admin.id,
                    "New Report Submitted",
                    f"New {report_type} report submitted for {target_type} ID {target_id}",
                    "report",
                    report.id,
                    "report"
                )
            
            flash('Report submitted successfully. Thank you for helping keep our community safe.')
            return redirect(url_for('skills'))
        
        return render_template('report.html', target_type=target_type, target_id=target_id)
    
    # Edit Profile
    @app.route('/edit_profile', methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        """Edit user profile"""
        if request.method == 'POST':
            current_user.name = request.form.get('name')
            current_user.email = request.form.get('email')
            current_user.location = request.form.get('location')
            current_user.gender = request.form.get('gender')
            current_user.bio = request.form.get('bio')
            
            # Handle photo upload
            if 'photo' in request.files:
                file = request.files['photo']
                if file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(f"user_{current_user.id}_{file.filename}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    current_user.profile_photo = filename
            
            db.session.commit()
            flash('Profile updated successfully!')
            return redirect(url_for('edit_profile'))
        
        return render_template('edit_profile.html')
    
    # Leaderboard
    @app.route('/leaderboard')
    def leaderboard():
        """Show leaderboard of top users"""
        # Get users with their stats
        users = User.query.filter_by(is_banned=False).all()
        
        for user in users:
            # Calculate exchange count
            user.exchanges_count = Exchange.query.filter_by(
                offering_user_id=user.id, status='Completed'
            ).count() + Exchange.query.filter_by(
                requesting_user_id=user.id, status='Completed'
            ).count()
            
            # Calculate skills count
            user.skills_count = Skill.query.filter_by(user_id=user.id).count()
        
        # Sort by rating and achievements
        leaderboard_users = sorted(users, key=lambda x: (x.total_rating, x.daily_tasks_completed), reverse=True)[:20]
        
        return render_template('leaderboard.html', leaderboard_users=leaderboard_users)
    
    # Notifications
    @app.route('/notifications')
    @login_required
    def notifications():
        """Show all notifications"""
        notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
        return render_template('notifications.html', notifications=notifications)
    
    # API Routes for Notifications
    @app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
    @login_required
    def mark_notification_read(notification_id):
        """Mark a notification as read"""
        notification = Notification.query.get_or_404(notification_id)
        if notification.user_id == current_user.id:
            notification.is_read = True
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    @app.route('/api/notifications/mark-all-read', methods=['POST'])
    @login_required
    def mark_all_notifications_read():
        """Mark all notifications as read"""
        Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
        db.session.commit()
        return jsonify({'success': True})
    
    # Helper function to create notifications
    def create_notification(user_id, title, message, notification_type, related_id=None, related_type=None):
        """Create a new notification"""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            related_id=related_id,
            related_type=related_type
        )
        db.session.add(notification)
        db.session.commit()
    
    # Update exchange feedback to create notifications and update ratings
    @app.route('/exchange/<int:exchange_id>/feedback', methods=['POST'])
    @login_required
    def exchange_feedback(exchange_id):
        exchange = Exchange.query.get_or_404(exchange_id)
        if exchange.status == 'Completed' and (exchange.offering_user_id == current_user.id or exchange.requesting_user_id == current_user.id):
            rating = int(request.form.get('rating'))
            feedback = request.form.get('feedback')
            
            exchange.rating = rating
            exchange.feedback = feedback
            
            # Update user ratings
            if exchange.offering_user_id == current_user.id:
                # Current user is rating the requesting user
                rated_user = User.query.get(exchange.requesting_user_id)
                rated_user.update_rating(rating)
                
                # Create notification for rated user
                create_notification(
                    exchange.requesting_user_id,
                    "New Rating Received",
                    f"You received a {rating}/5 rating for your skill exchange.",
                    "rating",
                    exchange.id,
                    "exchange"
                )
            else:
                # Current user is rating the offering user
                rated_user = User.query.get(exchange.offering_user_id)
                rated_user.update_rating(rating)
                
                # Create notification for rated user
                create_notification(
                    exchange.offering_user_id,
                    "New Rating Received",
                    f"You received a {rating}/5 rating for your skill exchange.",
                    "rating",
                    exchange.id,
                    "exchange"
                )
            
            db.session.commit()
            flash('Feedback submitted!')
        return redirect(url_for('dashboard'))
    
    # Update exchange creation to create notifications
    @app.route('/api/exchanges', methods=['POST'])
    @login_required
    def api_create_exchange():
        """API endpoint to create a new exchange proposal"""
        data = request.get_json()
        
        # Validate that the user is not trying to exchange with themselves
        offering_skill = Skill.query.get_or_404(data['offering_skill_id'])
        requesting_skill = Skill.query.get_or_404(data['requesting_skill_id'])
        
        if offering_skill.user_id == requesting_skill.user_id:
            return jsonify({'error': 'You cannot exchange with yourself'}), 400
        
        # Check if user already has a pending exchange for this skill
        existing_exchange = Exchange.query.filter_by(
            offering_user_id=current_user.id,
            requested_skill_id=data['requesting_skill_id'],
            status='Pending'
        ).first()
        
        if existing_exchange:
            return jsonify({'error': 'You already have a pending exchange for this skill'}), 400
        
        # Validate skill IDs before creating exchange
        if not data.get('offering_skill_id') or not data.get('requesting_skill_id'):
            return jsonify({'error': 'Invalid skill IDs provided'}), 400
        
        # Verify skills exist
        offering_skill = Skill.query.get(data['offering_skill_id'])
        requesting_skill = Skill.query.get(data['requesting_skill_id'])
        
        if not offering_skill or not requesting_skill:
            return jsonify({'error': 'One or both skills not found'}), 404
        
        exchange = Exchange(
            offering_user_id=current_user.id,
            requesting_user_id=requesting_skill.user_id,
            offered_skill_id=data['offering_skill_id'],
            requested_skill_id=data['requesting_skill_id'],
            message=data.get('message', ''),
            status='Pending'
        )
        
        try:
            db.session.add(exchange)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Exchange creation error: {e}")
            return jsonify({'error': 'Failed to create exchange'}), 500
        
        # Create notification for the skill owner
        create_notification(
            requesting_skill.user_id,
            "New Exchange Request",
            f"{current_user.name} wants to exchange skills with you!",
            "swap_request",
            exchange.id,
            "exchange"
        )
        
        return jsonify({
            'id': exchange.id,
            'status': exchange.status,
            'message': 'Exchange proposal created successfully'
        }), 201
    
    # Chat routes
    @app.route('/chat')
    @login_required
    def chat_list():
        """Show list of chat rooms"""
        chat_rooms = current_user.get_chat_rooms()
        return render_template('chat/list.html', chat_rooms=chat_rooms)
    
    @app.route('/chat/<int:user_id>')
    @login_required
    def start_chat(user_id):
        """Start or continue chat with a user"""
        if user_id == current_user.id:
            flash('You cannot chat with yourself!')
            return redirect(url_for('chat_list'))
        
        other_user = User.query.get_or_404(user_id)
        chat_room = current_user.get_or_create_chat_room(user_id)
        
        # Mark messages as read
        ChatMessage.query.filter_by(
            chat_room_id=chat_room.id,
            sender_id=other_user.id,
            is_read=False
        ).update({'is_read': True})
        db.session.commit()
        
        return render_template('chat/room.html', chat_room=chat_room, other_user=other_user)
    
    @app.route('/api/chat/<int:chat_room_id>/messages', methods=['GET'])
    @login_required
    def get_chat_messages(chat_room_id):
        """Get messages for a chat room"""
        chat_room = ChatRoom.query.get_or_404(chat_room_id)
        
        # Check if user is part of this chat room
        if chat_room.user1_id != current_user.id and chat_room.user2_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        messages = ChatMessage.query.filter_by(chat_room_id=chat_room_id).order_by(ChatMessage.created_at).all()
        
        return jsonify([{
            'id': msg.id,
            'sender_id': msg.sender_id,
            'message': msg.message,
            'created_at': msg.created_at.isoformat(),
            'is_mine': msg.sender_id == current_user.id
        } for msg in messages])
    
    @app.route('/api/chat/<int:chat_room_id>/send', methods=['POST'])
    @login_required
    def send_message(chat_room_id):
        """Send a message in a chat room"""
        chat_room = ChatRoom.query.get_or_404(chat_room_id)
        
        # Check if user is part of this chat room
        if chat_room.user1_id != current_user.id and chat_room.user2_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        message_text = request.json.get('message', '').strip()
        if not message_text:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Create new message
        message = ChatMessage(
            chat_room_id=chat_room_id,
            sender_id=current_user.id,
            message=message_text
        )
        
        # Update last message time
        chat_room.last_message_at = datetime.utcnow()
        
        db.session.add(message)
        db.session.commit()
        
        # Create notification for the other user
        other_user_id = chat_room.get_other_user(current_user.id).id
        create_notification(
            other_user_id,
            f"New message from {current_user.name}",
            message_text[:50] + "..." if len(message_text) > 50 else message_text,
            "chat_message",
            chat_room_id,
            "chat_room"
        )
        
        return jsonify({
            'id': message.id,
            'message': message.message,
            'created_at': message.created_at.isoformat(),
            'sender_id': message.sender_id
        }), 201
    
    @app.route('/api/chat/unread-count')
    @login_required
    def get_unread_chat_count():
        """Get unread chat messages count"""
        count = current_user.get_unread_chat_count()
        return jsonify({'count': count})
    
    # Availability routes
    @app.route('/availability')
    @login_required
    def availability():
        """Manage user availability"""
        availabilities = current_user.get_availability()
        return render_template('availability.html', availabilities=availabilities)
    
    @app.route('/availability/update', methods=['POST'])
    @login_required
    def update_availability():
        """Update user availability"""
        day_of_week = request.form.get('day_of_week')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        is_available = request.form.get('is_available') == 'true'
        
        if not day_of_week or not start_time_str or not end_time_str:
            flash('Please fill in all fields')
            return redirect(url_for('availability'))
        
        try:
            from datetime import time
            start_time = time.fromisoformat(start_time_str)
            end_time = time.fromisoformat(end_time_str)
            
            current_user.set_availability(day_of_week, start_time, end_time, is_available)
            flash('Availability updated successfully!')
        except Exception as e:
            flash(f'Error updating availability: {str(e)}')
        
        return redirect(url_for('availability'))
    
    @app.route('/api/availability/<int:user_id>')
    @login_required
    def get_user_availability(user_id):
        """Get availability for a specific user"""
        user = User.query.get_or_404(user_id)
        availabilities = user.get_availability()
        return jsonify([avail.to_dict() for avail in availabilities])
    
    @app.route('/exchange/<int:exchange_id>/schedule', methods=['GET', 'POST'])
    @login_required
    def schedule_exchange(exchange_id):
        """Schedule an exchange"""
        exchange = Exchange.query.get_or_404(exchange_id)
        
        # Check if user is part of this exchange
        if exchange.offering_user_id != current_user.id and exchange.requesting_user_id != current_user.id:
            flash('You are not authorized to schedule this exchange')
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            scheduled_date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
            start_time = time.fromisoformat(request.form.get('start_time'))
            end_time = time.fromisoformat(request.form.get('end_time'))
            location = request.form.get('location')
            meeting_type = request.form.get('meeting_type', 'in_person')
            meeting_link = request.form.get('meeting_link')
            notes = request.form.get('notes')
            
            # Create or update schedule
            schedule = ExchangeSchedule.query.filter_by(exchange_id=exchange_id).first()
            if not schedule:
                schedule = ExchangeSchedule(exchange_id=exchange_id)
                db.session.add(schedule)
            
            schedule.scheduled_date = scheduled_date
            schedule.start_time = start_time
            schedule.end_time = end_time
            schedule.location = location
            schedule.meeting_type = meeting_type
            schedule.meeting_link = meeting_link
            schedule.notes = notes
            
            db.session.commit()
            
            # Create notification for the other user
            other_user_id = exchange.requesting_user_id if exchange.offering_user_id == current_user.id else exchange.offering_user_id
            create_notification(
                other_user_id,
                "Exchange Scheduled",
                f"Your exchange has been scheduled for {scheduled_date.strftime('%B %d, %Y')} at {start_time.strftime('%I:%M %p')}",
                "exchange_scheduled",
                exchange_id,
                "exchange"
            )
            
            flash('Exchange scheduled successfully!')
            return redirect(url_for('dashboard'))
        
        # Get other user's availability
        other_user_id = exchange.requesting_user_id if exchange.offering_user_id == current_user.id else exchange.offering_user_id
        other_user = User.query.get(other_user_id)
        other_availability = other_user.get_availability() if other_user else []
        
        from datetime import date
        return render_template('schedule_exchange.html', 
                            exchange=exchange, 
                            other_user=other_user,
                            other_availability=other_availability,
                            today=date.today().isoformat())
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)