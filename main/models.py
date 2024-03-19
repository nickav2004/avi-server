from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class DataTable(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def row_count(self):
        return self.datarow_set.count()


class DataRow(models.Model):
    data_table = models.ForeignKey(DataTable, on_delete=models.CASCADE)
    global_time_ns = models.BigIntegerField(verbose_name="Global Time (ns from Epoch)")
    local_time_ms = models.FloatField(verbose_name="Local Time (ms from test)")
    upstream_pressure_psia = models.FloatField(verbose_name="Upstream Pressure (psia)")
    downstream_pressure_psia = models.FloatField(
        verbose_name="Downstream Pressure (psia)"
    )
    mass_flow_rate_kgs = models.FloatField(verbose_name="Mass Flow Rate (kg/s)")
    tank_volume_percent = models.FloatField(verbose_name="Tank Volume (%)")

    def __str__(self):
        return f"PressureData at {self.local_time_ms} ms"
