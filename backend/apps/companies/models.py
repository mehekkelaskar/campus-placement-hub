from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    official_message = models.TextField(blank=True, null=True,
                                       help_text='Official message from placement cell')
    jd_pdf = models.FileField(upload_to='jd_pdfs/', blank=True, null=True,
                              help_text='Job Description PDF')
    hiring_role = models.CharField(max_length=255, blank=True, null=True,
                                   help_text='e.g. Software Engineer, Data Analyst')
    eligibility = models.TextField(blank=True, null=True,
                                   help_text='Eligibility criteria (CGPA, branches, etc.)')
    apply_link = models.URLField(blank=True, null=True,
                                 help_text='Official application link')
    website = models.URLField(blank=True, null=True)
    deadline = models.DateTimeField(help_text='Application deadline')
    recruitment_process = models.TextField(blank=True, null=True,
                                           help_text='Recruitment process details')
    is_published = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'companies'

    def __str__(self):
        return self.name


class PlacementDrive(models.Model):
    STATUS_CHOICES = (
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('closed', 'Closed'),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='drives')
    drive_date = models.DateField()
    test_date = models.DateField(blank=True, null=True,
                                 help_text='Online test date')
    interview_date = models.DateField(blank=True, null=True,
                                      help_text='Interview date')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['drive_date']

    def __str__(self):
        return f"{self.company.name} - {self.drive_date}"
