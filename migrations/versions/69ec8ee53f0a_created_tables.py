"""created tables

Revision ID: 69ec8ee53f0a
Revises: 
Create Date: 2023-11-08 20:11:50.804580

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '69ec8ee53f0a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mentor',
    sa.Column('mentor_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('mentor_id')
    )
    op.create_table('student',
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('student_id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('assessment',
    sa.Column('assessment_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('time_limit', sa.String(length=50), nullable=True),
    sa.Column('mentor_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['mentor_id'], ['mentor.mentor_id'], ),
    sa.PrimaryKeyConstraint('assessment_id')
    )
    op.create_table('assessment_student_association',
    sa.Column('assessment_id', sa.Integer(), nullable=True),
    sa.Column('student_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['assessment_id'], ['assessment.assessment_id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['student.student_id'], )
    )
    op.create_table('assignment',
    sa.Column('assignment_id', sa.Integer(), nullable=False),
    sa.Column('assessment_id', sa.Integer(), nullable=True),
    sa.Column('mentor_id', sa.Integer(), nullable=True),
    sa.Column('student_id', sa.Integer(), nullable=True),
    sa.Column('is_accepted', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['assessment_id'], ['assessment.assessment_id'], ),
    sa.ForeignKeyConstraint(['mentor_id'], ['mentor.mentor_id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['student.student_id'], ),
    sa.PrimaryKeyConstraint('assignment_id')
    )
    op.create_table('invite',
    sa.Column('invite_id', sa.Integer(), nullable=False),
    sa.Column('assessment_id', sa.Integer(), nullable=True),
    sa.Column('mentor_id', sa.Integer(), nullable=True),
    sa.Column('student_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['assessment_id'], ['assessment.assessment_id'], ),
    sa.ForeignKeyConstraint(['mentor_id'], ['mentor.mentor_id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['student.student_id'], ),
    sa.PrimaryKeyConstraint('invite_id')
    )
    op.create_table('notification',
    sa.Column('notification_id', sa.Integer(), nullable=False),
    sa.Column('content', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('student_id', sa.Integer(), nullable=True),
    sa.Column('assessment_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['assessment_id'], ['assessment.assessment_id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['student.student_id'], ),
    sa.PrimaryKeyConstraint('notification_id')
    )
    op.create_table('question',
    sa.Column('question_id', sa.Integer(), nullable=False),
    sa.Column('text_question', sa.String(length=255), nullable=True),
    sa.Column('options', sa.String(length=255), nullable=True),
    sa.Column('correct_answer', sa.String(length=255), nullable=True),
    sa.Column('assessment_id', sa.Integer(), nullable=True),
    sa.Column('mentor_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['assessment_id'], ['assessment.assessment_id'], ),
    sa.ForeignKeyConstraint(['mentor_id'], ['mentor.mentor_id'], ),
    sa.PrimaryKeyConstraint('question_id')
    )
    op.create_table('answer',
    sa.Column('answer_id', sa.Integer(), nullable=False),
    sa.Column('option_a', sa.String(length=255), nullable=True),
    sa.Column('option_b', sa.String(length=255), nullable=True),
    sa.Column('option_c', sa.String(length=255), nullable=True),
    sa.Column('option_d', sa.String(length=255), nullable=True),
    sa.Column('question_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['question_id'], ['question.question_id'], ),
    sa.PrimaryKeyConstraint('answer_id')
    )
    op.create_table('feedback',
    sa.Column('feedback_id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=True),
    sa.Column('mentor_id', sa.Integer(), nullable=True),
    sa.Column('question_id', sa.Integer(), nullable=True),
    sa.Column('assessment_id', sa.Integer(), nullable=True),
    sa.Column('feedback', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['assessment_id'], ['assessment.assessment_id'], ),
    sa.ForeignKeyConstraint(['mentor_id'], ['mentor.mentor_id'], ),
    sa.ForeignKeyConstraint(['question_id'], ['question.question_id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['student.student_id'], ),
    sa.PrimaryKeyConstraint('feedback_id')
    )
    op.create_table('grade',
    sa.Column('grade_id', sa.Integer(), nullable=False),
    sa.Column('grade', sa.String(length=50), nullable=True),
    sa.Column('assessment_id', sa.Integer(), nullable=True),
    sa.Column('student_id', sa.Integer(), nullable=True),
    sa.Column('assignment_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['assessment_id'], ['assessment.assessment_id'], ),
    sa.ForeignKeyConstraint(['assignment_id'], ['assignment.assignment_id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['student.student_id'], ),
    sa.PrimaryKeyConstraint('grade_id')
    )
    op.create_table('response',
    sa.Column('response_id', sa.Integer(), nullable=False),
    sa.Column('assignment_id', sa.Integer(), nullable=True),
    sa.Column('question_id', sa.Integer(), nullable=True),
    sa.Column('student_id', sa.Integer(), nullable=True),
    sa.Column('answer_text', sa.String(length=255), nullable=True),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['assignment_id'], ['assignment.assignment_id'], ),
    sa.ForeignKeyConstraint(['question_id'], ['question.question_id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['student.student_id'], ),
    sa.PrimaryKeyConstraint('response_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('response')
    op.drop_table('grade')
    op.drop_table('feedback')
    op.drop_table('answer')
    op.drop_table('question')
    op.drop_table('notification')
    op.drop_table('invite')
    op.drop_table('assignment')
    op.drop_table('assessment_student_association')
    op.drop_table('assessment')
    op.drop_table('student')
    op.drop_table('mentor')
    # ### end Alembic commands ###
